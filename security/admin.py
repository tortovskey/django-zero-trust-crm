from django.contrib import admin

from .models import SecurityEvent, TrustedDevice


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'user', 'risk_level', 'ip_address', 'created_at')
    list_filter = ('event_type', 'risk_level', 'created_at')
    search_fields = ('user__username', 'description', 'ip_address')


@admin.register(TrustedDevice)
class TrustedDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'ip_address', 'is_trusted', 'last_seen_at')
    list_filter = ('is_trusted',)
    search_fields = ('name', 'user__username', 'ip_address', 'user_agent')
