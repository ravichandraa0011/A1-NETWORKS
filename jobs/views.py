from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Job
from .forms import JobForm
from django.db.models import Q


def job_list(request):
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')
    recommended_jobs = []

    if request.user.is_authenticated:
        query = Q()
        
        # 1. Direct Industry Match
        if request.user.industry:
            query |= Q(industry__icontains=request.user.industry)
            
        # 2. Precision Skill Matching (User's skills vs Job's required skills)
        if request.user.core_skills:
            skills = [skill.strip() for skill in request.user.core_skills.split(',') if skill.strip()]
            for skill in skills:
                # Checks if the user's skill is in the job's title OR the specific required_skills field
                query |= Q(title__icontains=skill) | Q(required_skills__icontains=skill)
                
        if query:
            recommended_jobs = Job.objects.filter(query, is_active=True).exclude(posted_by=request.user).distinct().order_by('-created_at')[:3]

    context = {
        'jobs': jobs,
        'recommended_jobs': recommended_jobs,
    }
    return render(request, 'jobs/job_list.html', context)   

@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            # Don't save to database just yet
            new_job = form.save(commit=False)
            # Attach the current logged-in user as the job poster
            new_job.posted_by = request.user
            new_job.save()
            return redirect('jobs:job_list')
    else:
        form = JobForm()
        
    return render(request, 'jobs/post_job.html', {'form': form})