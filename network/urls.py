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
    path('inbox/', views.inbox, name='inbox'),
    path('inbox/<str:username>/', views.inbox, name='inbox_chat'),
    path('user/<str:username>/', views.profile_view, name='profile'),

    # Connection Actions 
    path('user/<str:username>/connect/', views.send_request, name='send_request'),
    path('connection/accept/<int:connection_id>/', views.accept_request, name='accept_request'),
    path('connection/ignore/<int:connection_id>/', views.ignore_request, name='ignore_request'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
    # Post Actions
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    
    # Portfolio, Projects & Analytics (The missing links!)
    path('portfolio/<str:username>/', views.portfolio_maker, name='portfolio_maker'),
    path('add-project/', views.add_project, name='add_project'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('groups/tag/<str:hashtag>/', views.group_by_tag, name='group_by_tag'),
    # Add this line somewhere in your urlpatterns list:
    path('chatbot/respond/', views.chatbot_response, name='chatbot_respond'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    # Add these inside your urlpatterns = [ ... ]
    path('radar/', views.local_radar, name='local_radar'),
    path('toggle-radar/', views.toggle_availability, name='toggle_availability'),
    path('user/<str:username>/review/', views.leave_review, name='leave_review'),
    path('analytics/', views.profile_analytics, name='profile_analytics'),
    path('connect/<str:username>/', views.send_request, name='send_request'),
    path('invite/<str:username>/', views.invite_to_job, name='invite_to_job'),
    ]