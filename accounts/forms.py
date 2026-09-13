from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(label='Имя', required=False)
    last_name = forms.CharField(label='Фамилия', required=False)
    phone = forms.CharField(label='Телефон', required=False)
    department = forms.CharField(label='Отдел', required=False)
    mfa_enabled = forms.BooleanField(label='Включить демонстрационный MFA', required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'department', 'mfa_enabled']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            profile = user.profile
            profile.phone = self.cleaned_data.get('phone', '')
            profile.department = self.cleaned_data.get('department', '')
            profile.mfa_enabled = self.cleaned_data.get('mfa_enabled', False)
            profile.save()
        return user


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label='Имя', required=False)
    last_name = forms.CharField(label='Фамилия', required=False)
    email = forms.EmailField(label='Email', required=False)

    class Meta:
        model = Profile
        fields = ['department', 'phone', 'mfa_enabled']
        labels = {
            'department': 'Отдел',
            'phone': 'Телефон',
            'mfa_enabled': 'Демонстрационный MFA',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.instance.user
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name
        self.fields['email'].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()
            profile.save()
        return profile


class UserRoleForm(forms.ModelForm):
    is_active = forms.BooleanField(label='Активен в Django', required=False)

    class Meta:
        model = Profile
        fields = ['role', 'department', 'phone', 'is_active_profile', 'mfa_enabled']
        labels = {
            'role': 'Роль',
            'department': 'Отдел',
            'phone': 'Телефон',
            'is_active_profile': 'Активен в KOSTY',
            'mfa_enabled': 'Демонстрационный MFA',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_active'].initial = self.instance.user.is_active

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.is_active = self.cleaned_data['is_active']
        if commit:
            profile.user.save()
            profile.save()
        return profile
