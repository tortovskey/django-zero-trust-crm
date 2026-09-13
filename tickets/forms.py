from django import forms
from django.contrib.auth.models import User

from accounts.models import Profile
from accounts.rbac import ADMIN, MANAGER, USER, get_role

from .models import Ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['client', 'subject', 'description', 'status', 'priority', 'responsible_manager']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        managers = User.objects.filter(profile__role__in=[Profile.Role.ADMIN, Profile.Role.MANAGER])
        self.fields['responsible_manager'].queryset = managers
        if get_role(self.user) == USER:
            self.fields.pop('client')
            self.fields.pop('status')
            self.fields.pop('responsible_manager')


class TicketStatusForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'responsible_manager']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['responsible_manager'].queryset = User.objects.filter(
            profile__role__in=[Profile.Role.ADMIN, Profile.Role.MANAGER]
        )
