from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        # FIXED: Changed to 'mobile_number'
        fields = ('username', 'email', 'mobile_number', 'first_name', 'last_name', 'headline', 'industry')

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        # FIXED: Changed to 'mobile_number' and added the missing comma at the end!
        fields = (
            'first_name', 'last_name', 'headline', 'industry', 'mobile_number',
            'education', 'core_skills', 'interests',
            'profile_picture', 'banner_image', 'open_to_work', 
            'github_link', 'portfolio_website'
        )

        widgets = {
            # This tells HTML to bring up the number keypad on mobile devices
            'mobile_number': forms.TextInput(attrs={'type': 'tel', 'placeholder': '+91 9876543210'})
        }