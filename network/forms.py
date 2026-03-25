from django import forms
from .models import ProjectPortfolio

class ProjectForm(forms.ModelForm):
    class Meta:
        model = ProjectPortfolio
        # We only ask for these fields. 
        # 'owner' is set via the backend, and 'is_peer_reviewed' is for others to decide.
        fields = ['title', 'description', 'external_link']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your role and the outcome...'}),
            'external_link': forms.URLInput(attrs={'placeholder': 'https://github.com/... or https://...'})
        }