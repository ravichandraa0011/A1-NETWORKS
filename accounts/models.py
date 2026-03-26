from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Professional fields
    headline = models.CharField(max_length=150, blank=True, help_text="e.g., Software Engineer")
    industry = models.CharField(max_length=100, blank=True)
    
    # Trust Signal (Crucial for niche networks)
    is_industry_verified = models.BooleanField(default=False)

    # NEW FIELDS: Dynamic Portfolio Data
    education = models.TextField(blank=True, null=True, help_text="e.g., B.S. in Computer Science")
    core_skills = models.TextField(blank=True, null=True, help_text="e.g., Python, Django, Cloud Architecture")
    interests = models.TextField(blank=True, null=True, help_text="e.g., Cybersecurity, Open Source Development")

    # Visuals
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png', blank=True)
    banner_image = models.ImageField(upload_to='banners/', default='banners/default_banner.jpg', blank=True)
    
    # Status
    open_to_work = models.BooleanField(default=False)
    
    # Pro Links (Crucial for showcasing actual code and deployments)
    github_link = models.URLField(max_length=200, blank=True, null=True, help_text="Link to your GitHub profile")
    portfolio_website = models.URLField(max_length=200, blank=True, null=True, help_text="Link to your personal site")

    def __str__(self):
        return f"{self.first_name} {self.last_name} (@{self.username})"