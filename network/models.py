from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


# ─── USER PROFILE ───
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    headline = models.CharField(max_length=255, blank=True)
    is_available_today = models.BooleanField(default=False) 

    def __str__(self):
        return self.user.username


# ─── REVIEWS ───
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


# ─── 1. NETWORKING & CONNECTIONS ───
class Connection(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        status = "Accepted" if self.is_accepted else "Pending"
        return f"{self.sender.username} -> {self.receiver.username} ({status})"


# ─── PROFILE VIEWS (ANALYTICS) ───
class ProfileView(models.Model):
    # FIXED: Replaced "User" with settings.AUTH_USER_MODEL
    viewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='views_made')
    viewed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='views_received')
    timestamp = models.DateTimeField(auto_now_add=True)

    # FIXED: Removed the unique_together Meta class and the duplicate string method!
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
    external_link = models.URLField(blank=True, null=True) 
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
        unique_together = ('project', 'reviewer')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
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
    views = models.PositiveIntegerField(default=0)
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