from django.contrib import admin

from .models import VoiceSession
from config.admin_tools import export_as_csv


@admin.register(VoiceSession)
class VoiceSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_type', 'status', 'detected_language', 'confidence_score', 'processing_time_ms', 'created_at')
    list_filter = ('session_type', 'status', 'detected_language', 'created_at')
    search_fields = ('user__email', 'user__name', 'input_text', 'output_text', 'error_message')
    ordering = ('-created_at',)
    autocomplete_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    actions = (export_as_csv,)
