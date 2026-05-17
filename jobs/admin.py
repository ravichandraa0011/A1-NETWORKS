# Register your models here.
from django.contrib import admin
from .models import Job, JobApplication

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'posted_by', 'is_active', 'created_at')
    list_filter = ('is_active', 'worker_type', 'created_at')
    search_fields = ('title', 'company', 'location')
    
@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('applicant__username', 'job__title')