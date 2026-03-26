from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        # Added industry and required_skills to the list
        fields = ['title', 'company', 'location', 'industry', 'required_skills', 'salary_range', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g., Senior Cloud Engineer', 'class': 'form-control'}),
            'company': forms.TextInput(attrs={'placeholder': 'e.g., Tech Solutions Inc.', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g., Remote or Kalaburagi', 'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'placeholder': 'e.g., Information Technology', 'class': 'form-control'}),
            'required_skills': forms.TextInput(attrs={'placeholder': 'e.g., Django, Python, SQL', 'class': 'form-control'}),
            'salary_range': forms.TextInput(attrs={'placeholder': 'e.g., ₹10 LPA - ₹15 LPA', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe the role, responsibilities, and requirements...', 'rows': 5, 'class': 'form-control'}),
        }