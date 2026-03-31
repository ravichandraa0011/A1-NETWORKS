from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('post/', views.post_job, name='post_job'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('<int:job_id>/apply/', views.apply_to_job, name='apply_to_job'),
    path('manage/<int:app_id>/<str:action>/', views.manage_application, name='manage_app'),
    path('my-posts/', views.my_posted_jobs, name='my_posted_jobs'),
    path('<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('delete/<int:job_id>/', views.delete_job, name='delete_job'),
]