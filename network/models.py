from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    headline = models.CharField(max_length=255, blank=True)
    # The Toggle Switch for the Local Radar Feature
    is_available_today = models.BooleanField(default=False) 

    def __str__(self):
        return self.user.username
# ─── PASTE THIS REVIEW MODEL RIGHT BELOW YOUR PROFILE MODEL ───
class Review(models.Model):
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews_given', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews_received', on_delete=models.CASCADE)
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating} Stars for {self.receiver.username}"
# ──────────────────────────────────────────────────────────────
# ─── 1. NETWORKING & CONNECTIONS ───
class Connection(models.Model):
    # The person who sent the request
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE)
    # The person receiving the request
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
    # Status of the request
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents sending multiple requests to the same person
        unique_together = ('sender', 'receiver')

    def __str__(self):
        status = "Accepted" if self.is_accepted else "Pending"
        return f"{self.sender.username} -> {self.receiver.username} ({status})"


class ProfileView(models.Model):
    # The person who is looking at the profile
    viewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='views_made')
    # The person whose profile is being looked at
    viewed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile_views')
    # When it happened (auto-updates to the latest view time)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        # This prevents spam. If I view your profile 10 times today, it only counts as 1 recent view.
        unique_together = ('viewer', 'viewed_user')

    def __str__(self):
        return f"{self.viewer.username} viewed {self.viewed_user.username}"


# ─── 2. MESSAGING SYSTEM ───
class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"


# ─── 3. PORTFOLIOS & REVIEWS ───
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


# ─── 4. SOCIAL FEED & POSTS ───
class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0) # Tracks views
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    
    def __str__(self):
        return f"Post by {self.author.username}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# ─── 5. TOPIC GROUPS & CHAT ───
class TopicGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='joined_groups', blank=True)

    def __str__(self):
        return self.name


class GroupMessage(models.Model):
    group = models.ForeignKey(TopicGroup, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)