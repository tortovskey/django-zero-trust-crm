from django import forms
from django.utils import timezone

from .models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'full_name',
            'email',
            'phone',
            'address',
            'client_type',
            'personal_data_consent',
            'consent_date',
            'consent_status',
            'processing_purpose',
            'comment',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'comment': forms.Textarea(attrs={'rows': 3}),
            'consent_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('personal_data_consent') and not cleaned.get('consent_date'):
            cleaned['consent_date'] = timezone.localdate()
        return cleaned
