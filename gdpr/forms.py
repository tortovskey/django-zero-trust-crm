from django import forms

from .models import DataDeletionRequest


class DataDeletionRequestForm(forms.ModelForm):
    class Meta:
        model = DataDeletionRequest
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'reason': 'Причина запроса',
        }


class DataDeletionReviewForm(forms.ModelForm):
    class Meta:
        model = DataDeletionRequest
        fields = ['status', 'admin_comment']
        widgets = {
            'admin_comment': forms.Textarea(attrs={'rows': 4}),
        }
