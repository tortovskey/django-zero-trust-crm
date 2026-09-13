from django.contrib import admin

from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('number', 'subject', 'status', 'priority', 'client', 'responsible_manager', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('number', 'subject', 'client__full_name')
