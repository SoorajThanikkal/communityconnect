from django import forms
from .models import CreativeContent

class CreativeContentForm(forms.ModelForm):
    class Meta:
        model = CreativeContent
        fields = ['title', 'content_type', 'description', 'uploaded_file', 'video_url', 'thoughts']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'thoughts': forms.Textarea(attrs={'rows': 3}),
        }