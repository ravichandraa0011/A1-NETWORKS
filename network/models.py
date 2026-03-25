from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class Connection(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('blocked', 'Blocked'),
    )
    
    # The user initiating the connection
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_connections', on_delete=models.CASCADE)
    # The user receiving the request
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_connections', on_delete=models.CASCADE)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Prevent duplicate connection requests between the same two people
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"

class ProjectPortfolio(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='projects', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Links to GitHub, publications, or case studies
    external_link = models.URLField(blank=True, null=True) 
    
    # Another Trust Signal
    is_peer_reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.owner.username}"
    
class ProjectReview(models.Model):
    project = models.ForeignKey(ProjectPortfolio, related_name='reviews', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='given_reviews', on_delete=models.CASCADE)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user can only leave one review per project
        unique_together = ('project', 'reviewer')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Automatically verify the project once a peer reviews it
        if not self.project.is_peer_reviewed:
            self.project.is_peer_reviewed = True
            self.project.save()

    def __str__(self):
        return f"Review by {self.reviewer.username} on {self.project.title}"