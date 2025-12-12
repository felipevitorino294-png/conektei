from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profession', 'description', 'price', 'phone', 'photo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }