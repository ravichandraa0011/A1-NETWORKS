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
        fields = ('first_name', 'last_name', 'headline', 'industry')
        widgets = {
            'headline': forms.TextInput(attrs={'placeholder': 'e.g., Senior Renewables Engineer'}),
            'industry': forms.TextInput(attrs={'placeholder': 'e.g., Clean Energy'}),
        }