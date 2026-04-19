from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# Make sure to import Message from your network app
from network.models import Message 
from .models import Job, JobApplication
from .forms import JobForm
from django.http import JsonResponse


# --- 1. THE MAIN JOB BOARD ---
@login_required
def job_list(request):
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')
    recommended_jobs = []
    
    # Get a list of IDs for the jobs this specific user has already applied to
    applied_job_ids = JobApplication.objects.filter(applicant=request.user).values_list('job_id', flat=True)

    if request.user.is_authenticated:
        query = Q()
        if hasattr(request.user, 'industry') and request.user.industry:
            query |= Q(industry__icontains=request.user.industry)
            
        if hasattr(request.user, 'core_skills') and request.user.core_skills:
            skills = [skill.strip() for skill in request.user.core_skills.split(',') if skill.strip()]
            for skill in skills:
                query |= Q(title__icontains=skill) | Q(required_skills__icontains=skill)
                
        if query:
            recommended_jobs = Job.objects.filter(query, is_active=True).exclude(posted_by=request.user).distinct().order_by('-created_at')[:3]

    return render(request, 'jobs/job_list.html', {
        'jobs': jobs, 
        'recommended_jobs': recommended_jobs,
        'applied_job_ids': applied_job_ids 
    })


# --- 2. THE JOB DETAIL PAGE ---
@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Check if this user has already applied
    user_app = JobApplication.objects.filter(job=job, applicant=request.user).first()
    
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'user_app': user_app
    })


# --- 3. APPLY FOR A JOB LOGIC ---
@login_required
def apply_to_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    # Don't let users apply to their own jobs
    if job.posted_by != request.user:
        # get_or_create safely prevents double-applications
        JobApplication.objects.get_or_create(job=job, applicant=request.user)
    return redirect('jobs:job_detail', job_id=job.id)


# --- 4. POST A NEW JOB ---
@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            new_job = form.save(commit=False)
            new_job.posted_by = request.user
            
            # Manually grab the custom worker_type from the HTML datalist
            worker_type = request.POST.get('worker_type')
            if worker_type:
                new_job.worker_type = worker_type
                
            new_job.save()
            return redirect('jobs:job_list')
    else:
        form = JobForm()
    return render(request, 'jobs/post_job.html', {'form': form})


# --- 5. EDIT AN EXISTING JOB ---
@login_required
def edit_job(request, job_id):
    # Fetch the job and ensure ONLY the creator can edit it
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            updated_job = form.save(commit=False)
            
            # Update the custom worker_type
            worker_type = request.POST.get('worker_type')
            if worker_type:
                updated_job.worker_type = worker_type
                
            updated_job.save()
            return redirect('jobs:job_detail', job_id=job.id)
    else:
        form = JobForm(instance=job)
        
    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})


# --- 6. EMPLOYER DASHBOARD (THE FIXED VIEW) ---
@login_required
def my_posted_jobs(request):
    # Fetch all jobs posted by the logged-in user
    my_jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')    
    
    context = {
        'my_jobs': my_jobs,
    }
    return render(request, 'jobs/my_jobs.html', context)


# --- 7. ACCEPT / REJECT APPLICANTS ---
@login_required
def manage_application(request, app_id, action):
    # Ensure the person managing the app is the one who posted the job
    application = get_object_or_404(JobApplication, id=app_id, job__posted_by=request.user)
    
    if action == 'accept':
        application.status = 'accepted'
        application.save()
        # Automatically send a chat message to the applicant!
        Message.objects.create(
            sender=request.user,
            receiver=application.applicant,
            content=f"Hello! I've accepted your application for '{application.job.title}'. Let's discuss the details here."
        )
    elif action == 'reject':
        application.status = 'rejected'
        application.save()
        
    return redirect('jobs:job_detail', job_id=application.job.id)


# --- 8. DELETE AN EXISTING JOB ---
@login_required
def delete_job(request, job_id):
    # Fetch the job and ensure ONLY the creator can delete it
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    
    if request.method == 'POST':
        job.delete()
        
    # Redirect back to their dashboard so they see the job is gone
    return redirect('jobs:my_posted_jobs')
@login_required
def withdraw_application(request, job_id):
    if request.method == 'POST':
        # Find the specific job and the user's application for it
        job = get_object_or_404(Job, id=job_id)
        application = get_object_or_404(JobApplication, job=job, applicant=request.user)
        
        # Only allow withdrawal if the employer hasn't processed it yet
        if application.status == 'pending':
            application.delete()
            return JsonResponse({"status": "withdrawn", "message": "Application withdrawn."})
        else:
            return JsonResponse({"status": "error", "message": "Cannot withdraw processed applications."})
            
    return JsonResponse({"status": "error", "message": "Invalid method."})