from django.contrib import admin
from .models import Profile, Review, Connection, ProjectPortfolio, Post, TopicGroup

# ─── 1. USER PROFILES MASTER TABLE ───
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # What columns show up in the table
    list_display = ('user', 'get_first_name', 'get_last_name', 'is_available_today', 'headline')
    
    # Creates a filter sidebar on the right
    list_filter = ('is_available_today',)
    
    # Creates a search bar at the top!
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'headline')
    
    # Pull data from the attached User model
    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'


# ─── 2. REPUTATION & REVIEWS MASTER TABLE ───
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('receiver', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('receiver__username', 'reviewer__username', 'comment')
    # Shows the newest reviews at the top automatically
    ordering = ('-created_at',) 


# ─── 3. PORTFOLIOS & PROJECTS ───
@admin.register(ProjectPortfolio)
class ProjectPortfolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_peer_reviewed', 'created_at')
    list_filter = ('is_peer_reviewed', 'created_at')
    search_fields = ('title', 'owner__username', 'description')


# ─── 4. CONNECTIONS ───
@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'is_accepted', 'created_at')
    list_filter = ('is_accepted',)
    search_fields = ('sender__username', 'receiver__username')


# ─── 5. POSTS (SOCIAL FEED) ───
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'views', 'created_at')
    search_fields = ('author__username', 'content')
    ordering = ('-created_at',)


# ─── 6. TOPIC GROUPS ───
@admin.register(TopicGroup)
class TopicGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_member_count')
    search_fields = ('name', 'description')

    def get_member_count(self, obj):
        return obj.members.count()
    get_member_count.short_description = 'Total Members'