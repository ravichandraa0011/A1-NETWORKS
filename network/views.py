import json
import re
from datetime import timedelta

from django.db.models import Q, Sum, Count, Avg
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from google import genai 

# Import your network models
from .models import (
    Profile, Review, ProjectPortfolio, Connection, 
    ProfileView, Message, Post, Comment, TopicGroup
)
from .forms import ProjectForm

# Import the Job models from your jobs app
from jobs.models import Job, JobApplication

User = get_user_model()


# ─── FEED & POSTS ───────────────────────────────────────
@login_required
def feed(request):
    latest_jobs = Job.objects.filter(is_active=True).exclude(posted_by=request.user).order_by('-created_at')[:5]
    
    pending_applications = JobApplication.objects.filter(
        job__posted_by=request.user, 
        status='pending'
    ).order_by('-created_at')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            post = Post.objects.create(author=request.user, content=content)
            
            hashtags = re.findall(r'#(\w+)', content)
            for tag in hashtags:
                group = TopicGroup.objects.filter(name__iexact=tag).first()
                if not group:
                    group = TopicGroup.objects.create(
                        name=tag, 
                        description=f"Community driven discussion about #{tag}"
                    )
                if request.user not in group.members.all():
                    group.members.add(request.user)
                    
            return redirect('network:feed')
    
    posts = Post.objects.all().order_by('-created_at')
    for post in posts:
        post.views += 1
        post.save()

    context = {
        'posts': posts,
        'latest_jobs': latest_jobs,
        'pending_applications': pending_applications,
    }
    return render(request, 'network/feed.html', context)

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('network:feed')

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        post.delete()
    return redirect('network:feed')

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)
    return redirect('network:feed')


# ─── CONNECTIONS & NETWORK ─────────────────────────────
@login_required
def my_network(request):
    pending_invites = Connection.objects.filter(receiver=request.user, is_accepted=False).order_by('-created_at')
    connections_records = Connection.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)), 
        is_accepted=True
    )
    
    connected_users = []
    for conn in connections_records:
        connected_users.append(conn.receiver if conn.sender == request.user else conn.sender)

    context = {
        'pending_invites': pending_invites,
        'connected_users': connected_users,
        'invite_count': pending_invites.count(),
    }
    return render(request, 'network/my_network.html', context)

@login_required
def send_request(request, username):
    if request.method == 'POST':
        target_user = get_object_or_404(User, username=username)
        
        if target_user == request.user:
            return JsonResponse({"status": "error", "message": "Cannot connect with yourself."})
            
        connection = Connection.objects.filter(sender=request.user, receiver=target_user).first()
        
        if connection:
            if not connection.is_accepted:
                connection.delete()
                return JsonResponse({"status": "withdrawn", "message": "Request withdrawn."})
            else:
                return JsonResponse({"status": "info", "message": "You are already connected."})
        else:
            reverse_conn = Connection.objects.filter(sender=target_user, receiver=request.user).exists()
            if reverse_conn:
                 return JsonResponse({"status": "info", "message": "They already sent you a request!"})
                 
            Connection.objects.create(sender=request.user, receiver=target_user, is_accepted=False)
            return JsonResponse({"status": "sent", "message": "Request sent!"})
            
    return JsonResponse({"status": "error", "message": "Invalid request."})

@login_required
def accept_request(request, connection_id):
    if request.method == 'POST':
        connection = get_object_or_404(Connection, id=connection_id, receiver=request.user, is_accepted=False)
        connection.is_accepted = True
        connection.save()
    return redirect('network:my_network')

@login_required
def ignore_request(request, connection_id):
    if request.method == 'POST':
        connection = get_object_or_404(Connection, id=connection_id, receiver=request.user, is_accepted=False)
        connection.delete()
    return redirect('network:my_network')


# ─── DIRECT MESSAGING ──────────────────────────────────
@login_required
def inbox(request, username=None):
    connections = Connection.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)) & Q(is_accepted=True)
    )
    contacts = [conn.receiver if conn.sender == request.user else conn.sender for conn in connections]

    active_contact = None
    messages_list = []

    if username:
        active_contact = get_object_or_404(User, username=username)
        messages_list = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=active_contact)) |
            (Q(sender=active_contact) & Q(receiver=request.user))
        ).order_by('timestamp')
        messages_list.filter(receiver=request.user).update(is_read=True)

    if request.method == 'POST' and active_contact:
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, receiver=active_contact, content=content)
            return redirect('network:inbox_chat', username=active_contact.username)

    return render(request, 'network/inbox.html', {
        'contacts': contacts,
        'active_contact': active_contact,
        'messages': messages_list,
    })


# ─── DIRECTORY & PROFILE ──────────────────────────────
@login_required
def directory(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(
        is_active=True, 
        is_superuser=False
    ).exclude(id=request.user.id)
    
    if query:
        users = users.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(profile__headline__icontains=query)
        )
    
    my_connections = Connection.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    )
    
    connected_users = []
    pending_users = []
    
    for conn in my_connections:
        other_user = conn.receiver if conn.sender == request.user else conn.sender
        if conn.is_accepted:
            connected_users.append(other_user)
        else:
            pending_users.append(other_user)

    users = users.order_by('first_name')
    
    context = {
        'users': users,
        'query': query,
        'connected_users': connected_users,
        'pending_users': pending_users,
    }
    return render(request, 'network/directory.html', context)

@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    # Track View Logic
    if request.user != profile_user:
        time_threshold = timezone.now() - timedelta(hours=24)
        recent_view = ProfileView.objects.filter(
            viewer=request.user, 
            viewed_user=profile_user,
            timestamp__gte=time_threshold
        ).exists()

        if not recent_view:
            ProfileView.objects.create(viewer=request.user, viewed_user=profile_user)

    connection = Connection.objects.filter(
        (Q(sender=request.user) & Q(receiver=profile_user)) | 
        (Q(sender=profile_user) & Q(receiver=request.user))
    ).first()

    connection_status = None
    if connection:
        if connection.is_accepted:
            connection_status = 'accepted'
        else:
            connection_status = 'sent' if connection.sender == request.user else 'received'

    user_posts = Post.objects.filter(author=profile_user).order_by('-created_at')
    user_jobs = Job.objects.filter(posted_by=profile_user, is_active=True).order_by('-created_at')
    projects = ProjectPortfolio.objects.filter(owner=profile_user).prefetch_related('reviews__reviewer').order_by('-created_at')

    # ─── NEW: FETCH REVIEWS & CHECK STATUS ───
    user_reviews = Review.objects.filter(receiver=profile_user).order_by('-created_at')
    
    has_reviewed = False
    if request.user.is_authenticated and request.user != profile_user:
        has_reviewed = Review.objects.filter(reviewer=request.user, receiver=profile_user).exists()
        
    average_rating = user_reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    context = {
        'profile_user': profile_user,
        'connection_status': connection_status,
        'connection': connection,
        'user_posts': user_posts, 
        'user_jobs': user_jobs,
        'projects': projects,
        'user_reviews': user_reviews,                  # Pass reviews to HTML
        'has_reviewed': has_reviewed,                  # Pass hide/show status
        'average_rating': round(average_rating, 1),    # Pass the math
    }
    return render(request, 'network/profile.html', context)


# ─── LOCAL RADAR ──────────────────────────────────────
@login_required
def toggle_availability(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    profile.is_available_today = not profile.is_available_today
    profile.save()
    
    status = "ON" if profile.is_available_today else "OFF"
    messages.success(request, f"Your Local Radar is now {status}.")
    return redirect(request.META.get('HTTP_REFERER', 'network:my_network'))

@login_required
def local_radar(request):
    available_workers = Profile.objects.filter(is_available_today=True).exclude(user=request.user).select_related('user')
    
    my_connections = Connection.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
    connected_users = [conn.receiver if conn.sender == request.user else conn.sender for conn in my_connections if conn.is_accepted]
    pending_users = [conn.receiver if conn.sender == request.user else conn.sender for conn in my_connections if not conn.is_accepted]
    
    my_jobs = Job.objects.filter(posted_by=request.user, is_active=True)

    context = {
        'available_workers': available_workers,
        'connected_users': connected_users,
        'pending_users': pending_users,
        'my_jobs': my_jobs,
    }
    return render(request, 'network/radar.html', context)

@login_required
def invite_to_job(request, username):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            job_id = data.get('job_id')
            target_user = get_object_or_404(User, username=username)
            job = get_object_or_404(Job, id=job_id, posted_by=request.user)

            Connection.objects.get_or_create(
                sender=request.user, 
                receiver=target_user,
                defaults={'is_accepted': False}
            )

            invite_text = f"Hi {target_user.first_name}! I saw you on the Local Radar and would love to invite you to apply for my open role: {job.title}."
            Message.objects.create(sender=request.user, receiver=target_user, content=invite_text)

            return JsonResponse({'status': 'success', 'message': 'Invitation sent!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


# ─── GROUPS ───────────────────────────────────────────
@login_required
def topic_groups(request):
    query = request.GET.get('q', '')
    if query:
        groups = TopicGroup.objects.filter(name__icontains=query)
    else:
        groups = TopicGroup.objects.all()
        
    return render(request, 'network/groups.html', {'groups': groups, 'query': query})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(TopicGroup, id=group_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            if f"#{group.name.lower()}" not in content.lower():
                content += f" #{group.name}"
                
            Post.objects.create(author=request.user, content=content)
            
            if request.user not in group.members.all():
                group.members.add(request.user)
        return redirect('network:group_detail', group_id=group.id)
    
    messages_list = Post.objects.filter(content__icontains=f"#{group.name}").order_by('-created_at')
    return render(request, 'network/group_detail.html', {'group': group, 'messages': messages_list})

@login_required
def group_by_tag(request, hashtag):
    group = TopicGroup.objects.filter(name__iexact=hashtag).first()
    if not group:
        group = TopicGroup.objects.create(name=hashtag, description=f"Community driven discussion about #{hashtag}")
    return redirect('network:group_detail', group_id=group.id)


# ─── PORTFOLIO & REVIEWS ─────────────────────────────
@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            return redirect('network:profile', username=request.user.username)
    else:
        form = ProjectForm()
    return render(request, 'network/add_project.html', {'form': form})

@login_required
def portfolio_maker(request, username):
    profile_user = get_object_or_404(User, username=username)
    projects = ProjectPortfolio.objects.filter(owner=profile_user).prefetch_related('reviews__reviewer').order_by('-created_at')
    return render(request, 'network/portfolio.html', {'profile_user': profile_user, 'projects': projects})

@login_required
def leave_review(request, username):
    receiver = get_object_or_404(User, username=username)
    
    if request.user == receiver:
        messages.error(request, "You cannot review yourself.")
        return redirect('network:profile', username=username)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        if rating:
            Review.objects.create(
                reviewer=request.user,
                receiver=receiver,
                rating=int(rating),
                comment=comment
            )
            messages.success(request, f"Review submitted for {receiver.first_name}!")
            
    return redirect('network:profile', username=username)


# ─── ANALYTICS ────────────────────────────────────────
@login_required
def analytics_dashboard(request):
    total_post_views = Post.objects.filter(author=request.user).aggregate(Sum('views'))['views__sum'] or 0
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    daily_views = ProfileView.objects.filter(
        viewed_user=request.user,
        timestamp__gte=seven_days_ago
    ).annotate(date=TruncDate('timestamp')) \
     .values('date') \
     .annotate(count=Count('id')) \
     .order_by('date')

   # ... your existing logic above ...
    dates = [(seven_days_ago + timedelta(days=i)).strftime('%b %d') for i in range(8)]
    counts_dict = {dv['date'].strftime('%b %d'): dv['count'] for dv in daily_views if dv['date']}
    chart_data = [counts_dict.get(d, 0) for d in dates]

    recent_views = ProfileView.objects.filter(viewed_user=request.user).order_by('-timestamp')[:10]

    context = {
        'total_post_views': total_post_views,
        'view_count': recent_views.count(),
        'recent_views': recent_views,
        'dates': dates,               # Removed json.dumps!
        'chart_data': chart_data      # Removed json.dumps!
    }
    return render(request, 'network/analytics.html', context)

# ─── AI CHATBOT ───────────────────────────────────────
@login_required
def chatbot_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_msg = data.get('message', '').strip()
            
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            models_to_try = [
                'gemini-2.5-flash-lite', 
                'gemini-2.5-flash',
                'gemini-flash-latest',
                'gemini-3.1-flash-lite-preview'
            ]
            
            response_text = None
            
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=f"You are the A1 Networks Assistant. User {request.user.first_name} says: {user_msg}"
                    )
                    if response and response.text:
                        response_text = response.text
                        print(f"--- SUCCESS: Connected via {model_name} ---")
                        break
                except Exception as model_err:
                    print(f"--- {model_name} failed: {str(model_err)[:50]}... ---")
                    continue

            if not response_text:
                if "group" in user_msg.lower():
                    response_text = "To create a group, just use a #hashtag in your Feed! Our system auto-generates the community page."
                else:
                    response_text = "I'm currently in 'Local Assistant' mode while the Gemini 2.5 API resets its quota. How can I help?"

            return JsonResponse({'reply': response_text})

        except Exception as e:
            print(f"--- SYSTEM ERROR: {e} ---")
            return JsonResponse({'reply': "Rebooting my AI brain. Please try again in 10 seconds!"})

    return JsonResponse({'error': 'POST only'}, status=400)
@login_required
def analyze_profile(request, username):
    if request.user.username != username:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method == 'POST':
        try:
            # 1. Gather the User's Data (Safely!)
            profile = getattr(request.user, 'profile', None)
            headline = profile.headline if profile else "No headline"
            
            # Get their project titles
            projects = ProjectPortfolio.objects.filter(owner=request.user)
            project_list = ", ".join([p.title for p in projects]) if projects else "No projects added yet"

            # 2. Build the exact Prompt for Gemini
            ai_prompt = f"""
            You are a tough but supportive Senior Tech Recruiter in Silicon Valley. 
            Analyze this candidate's profile:
            - Name: {request.user.first_name}
            - Headline: {headline}
            - Projects: {project_list}

            Format your response exactly like this:
            **🔥 The Roast:** (Give 1 short, witty, slightly critical sentence about what is weak or missing in their profile it should funny and also roast).
            **🚀 The Boost:** (Give 2 actionable, specific bullet points on what they should build or add next to get hired).
            """

            # 3. Call Gemini with the Fallback Loop
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            models_to_try = [
                'gemini-2.5-flash-lite', 
                'gemini-2.5-flash',
                'gemini-flash-latest'
            ]
            
            response_text = None
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=ai_prompt
                    )
                    if response and response.text:
                        response_text = response.text
                        break # It worked!
                except Exception as model_err:
                    print(f"Model {model_name} failed: {model_err}")
                    continue 

            if not response_text:
                return JsonResponse({'error': 'All AI models are currently busy. Please try again in 1 minute!'})

            # Format the text with HTML so it looks pretty
            formatted_text = response_text.replace('\n', '<br>')
            return JsonResponse({'analysis': formatted_text})

        except Exception as e:
            print(f"System Error: {e}")
            return JsonResponse({'error': 'The AI is currently resting. Try again in a moment!'})

    return JsonResponse({'error': 'Invalid request'}, status=400)