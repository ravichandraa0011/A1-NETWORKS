from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Professional fields
    headline = models.CharField(max_length=150, blank=True, help_text="e.g., Senior Renewable Energy Engineer")
    industry = models.CharField(max_length=100, blank=True)
    
    # Trust Signal (Crucial for niche networks)
    is_industry_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (@{self.username})"