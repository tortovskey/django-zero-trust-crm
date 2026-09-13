from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'is_active_profile', 'mfa_enabled', 'last_login_at')
    list_filter = ('role', 'is_active_profile', 'mfa_enabled')
    search_fields = ('user__username', 'user__email', 'department', 'phone')
