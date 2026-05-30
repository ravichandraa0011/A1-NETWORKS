from django.urls import path
from . import views

app_name = 'network'

urlpatterns = [
    # Main Pages
    path('', views.directory, name='directory'),
    path('mynetwork/', views.my_network, name='my_network'),
    path('feed/', views.feed, name='feed'),
    path('groups/', views.topic_groups, name='groups'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/tag/<str:hashtag>/', views.group_by_tag, name='group_by_tag'),
    path('inbox/', views.inbox, name='inbox'),
    path('inbox/<str:username>/', views.inbox, name='inbox_chat'),
    
    # Profile & Portfolio
    path('user/<str:username>/', views.profile_view, name='profile'),
    path('user/<str:username>/review/', views.leave_review, name='leave_review'),
    path('profile/<str:username>/analyze/', views.analyze_profile, name='analyze_profile'),
    path('portfolio/<str:username>/', views.portfolio_maker, name='portfolio_maker'),
    
    # Connection Actions 
    path('user/<str:username>/connect/', views.send_request, name='send_request'),
    path('connection/accept/<int:connection_id>/', views.accept_request, name='accept_request'),
    path('connection/ignore/<int:connection_id>/', views.ignore_request, name='ignore_request'),
    
    # Post Actions
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    
    # Projects
    path('add-project/', views.add_project, name='add_project'),
    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    
    # Radar & Jobs
    path('radar/', views.local_radar, name='local_radar'),
    path('toggle-radar/', views.toggle_availability, name='toggle_availability'),
    path('invite/<str:username>/', views.invite_to_job, name='invite_to_job'),
    
    # Analytics & Chatbot
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('chatbot/respond/', views.chatbot_response, name='chatbot_respond'),
]