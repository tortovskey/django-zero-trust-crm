from django.contrib import admin

from .models import ConsentRecord, DataDeletionRequest


@admin.register(DataDeletionRequest)
class DataDeletionRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'client', 'status', 'requested_at')
    list_filter = ('status', 'requested_at')
    search_fields = ('user__username', 'client__full_name', 'reason')


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ('client', 'purpose', 'is_given', 'recorded_at')
    list_filter = ('is_given', 'recorded_at')
    search_fields = ('client__full_name', 'purpose')
