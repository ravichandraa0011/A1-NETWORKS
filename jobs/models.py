from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class Job(models.Model):
    # Standard Fields
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=150)
    
    # Matching & Worker Type
    # This stores the choice from your 50+ profession list
    worker_type = models.CharField(max_length=100, blank=True, null=True) 
    industry = models.CharField(max_length=100, blank=True, null=True)
    required_skills = models.CharField(max_length=255, blank=True, null=True)
    
    description = models.TextField()
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True, help_text="e.g., +91 9876543210")

    def __str__(self):
        return f"{self.title} at {self.company}"

# FIXED: Move this outside of the Job class
class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'), 
        ('accepted', 'Accepted'), 
        ('rejected', 'Rejected')
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents a worker from applying to the same job twice
        unique_together = ('job', 'applicant') 

    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title}"
