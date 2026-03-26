from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'headline', 'industry')

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        # Added the visual and pro fields to the end of this list
        fields = (
            'first_name', 'last_name', 'headline', 'industry', 
            'education', 'core_skills', 'interests',
            'profile_picture', 'banner_image', 'open_to_work', 
            'github_link', 'portfolio_website'
        )