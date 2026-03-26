from django.db import models
from django.conf import settings

class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=150, help_text="e.g., Remote, Bengaluru, etc.")
    
    # --- NEW: ALGORITHM MATCHING FIELDS ---
    industry = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Software, Cloud Computing")
    required_skills = models.CharField(max_length=255, blank=True, null=True, help_text="Comma separated (e.g., Python, Django, AWS)")
    # --------------------------------------
    
    description = models.TextField()
    salary_range = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., ₹8,000,000 - ₹12,000,000 (Optional)")
    
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.company}"