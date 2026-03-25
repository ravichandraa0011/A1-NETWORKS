import json
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ProjectPortfolio, Connection, ProjectReview # Added ProjectReview
from django.contrib.auth import get_user_model

User = get_user_model()
@login_required
def my_network(request):
    # 1. Incoming requests waiting for the user's approval
    pending_requests = Connection.objects.filter(
        to_user=request.user, 
        status='pending'
    ).select_related('from_user')

    # 2. Active connections (where the user is either the sender or receiver)
    active_connections = Connection.objects.filter(
        (Q(from_user=request.user) | Q(to_user=request.user)),
        status='accepted'
    ).select_related('from_user', 'to_user')

    context = {
        'pending_requests': pending_requests,
        'active_connections': active_connections,
    }
    return render(request, 'network/my_network.html', context)

@require_POST
@login_required
def update_connection(request, connection_id):
    # Security check: Ensure the connection exists, is pending, AND the logged-in user is the receiver
    connection = get_object_or_404(Connection, id=connection_id, to_user=request.user, status='pending')
    
    try:
        data = json.loads(request.body)
        action = data.get('action')

        if action == 'accept':
            connection.status = 'accepted'
            connection.save()
            return JsonResponse({'status': 'accepted'})
        elif action == 'decline':
            # We can either delete it or mark it declined. Deleting keeps the DB cleaner for MVP.
            connection.delete() 
            return JsonResponse({'status': 'declined'})
            
        return JsonResponse({'error': 'Invalid action'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

@login_required
def directory(request):
    # Get the search query from the URL (e.g., ?q=engineer)
    query = request.GET.get('q', '')
    
    # Start with all active users, excluding the current logged-in user
    users = User.objects.filter(is_active=True).exclude(id=request.user.id)
    
    if query:
        # Filter users based on first name, last name, or headline
        users = users.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(headline__icontains=query)
        )
    
    # Order by verified users first, then alphabetically
    users = users.order_by('-is_industry_verified', 'first_name')

    context = {
        'users': users,
        'query': query,
    }
    return render(request, 'network/directory.html', context)

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
@require_POST
def handle_connection(request, username):
    target_user = get_object_or_404(User, username=username)
    
    if request.user == target_user:
        return JsonResponse({'error': 'Cannot connect with yourself'}, status=400)

    connection = Connection.objects.filter(
        (Q(from_user=request.user) & Q(to_user=target_user)) |
        (Q(from_user=target_user) & Q(to_user=request.user))
    ).first()

    if not connection:
        Connection.objects.create(from_user=request.user, to_user=target_user, status='pending')
        return JsonResponse({'status': 'pending', 'action': 'created'})

    connection.delete()
    return JsonResponse({'status': 'none', 'action': 'deleted'})

def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    # OPTIMIZED: We added prefetch_related to load reviews efficiently
    projects = ProjectPortfolio.objects.filter(owner=profile_user).prefetch_related('reviews__reviewer').order_by('-created_at')
    
    connection_status = None
    if request.user.is_authenticated and request.user != profile_user:
        connection = Connection.objects.filter(
            from_user__in=[request.user, profile_user],
            to_user__in=[request.user, profile_user]
        ).first()
        if connection:
            connection_status = connection.status

    context = {
        'profile_user': profile_user,
        'projects': projects,
        'connection_status': connection_status,
    }
    return render(request, 'network/profile.html', context)


@require_POST
@login_required
def add_project_review(request, project_id):
    project = get_object_or_404(ProjectPortfolio, id=project_id)

    # 1. Prevent self-reviewing
    if project.owner == request.user:
        return JsonResponse({'error': 'You cannot review your own project.'}, status=400)

    # 2. Security Check: Are they actually connected?
    is_connected = Connection.objects.filter(
        (Q(from_user=request.user, to_user=project.owner) | Q(from_user=project.owner, to_user=request.user)),
        status='accepted'
    ).exists()

    if not is_connected:
        return JsonResponse({'error': 'You must be an accepted connection to leave a peer review.'}, status=403)

    try:
        data = json.loads(request.body)
        review_text = data.get('review_text', '').strip()

        if not review_text:
            return JsonResponse({'error': 'Review text cannot be empty.'}, status=400)

        # 3. Create the review (get_or_create prevents duplicates)
        review, created = ProjectReview.objects.get_or_create(
            project=project,
            reviewer=request.user,
            defaults={'review_text': review_text}
        )

        if not created:
            return JsonResponse({'error': 'You have already reviewed this project.'}, status=400)

        return JsonResponse({
            'status': 'success',
            'reviewer_name': f"{request.user.first_name} {request.user.last_name}",
            'review_text': review_text
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid data format.'}, status=400)