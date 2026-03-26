from django.urls import path
from . import views

app_name = 'network'

urlpatterns = [
    # Example URL: /user/johndoe/
    path('', views.directory, name='directory'), 
    path('user/<str:username>/', views.profile_view, name='profile'),
    path('user/<str:username>/connect/', views.handle_connection, name='handle_connection'),
    path('project/add/', views.add_project, name='add_project'),
    path('', views.directory, name='directory'), 
    # Add this right below your directory path
    path('search/', views.search_view, name='search'),
    # Add these new routes:
    path('mynetwork/', views.my_network, name='my_network'),
    path('connection/<int:connection_id>/update/', views.update_connection, name='update_connection'),
    path('project/<int:project_id>/review/', views.add_project_review, name='add_project_review'),
    # Add this line right below your existing profile view
    path('user/<str:username>/portfolio/', views.portfolio_maker, name='portfolio_maker'),
    # Add this right below your my_network path
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    # Add these right above your analytics path
    path('messages/', views.inbox, name='inbox'),
    path('messages/<str:username>/', views.chat_view, name='chat_view'),
]

