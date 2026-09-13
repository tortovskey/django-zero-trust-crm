from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'client_type', 'personal_data_consent', 'consent_status')
    list_filter = ('client_type', 'personal_data_consent', 'consent_status')
    search_fields = ('full_name', 'email', 'phone')
