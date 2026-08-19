from django.contrib import admin

from .models import Application
from config.admin_tools import export_as_csv


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'employee', 'status', 'ai_match_score', 'interview_date', 'created_at')
    list_filter = ('status', 'interview_type', 'created_at')
    search_fields = ('job__title', 'employee__email', 'employee__name', 'interview_location')
    ordering = ('-created_at',)
    autocomplete_fields = ('job', 'employee')
    readonly_fields = ('created_at', 'updated_at')
    actions = ('mark_under_review', 'mark_hired', 'mark_rejected', export_as_csv)

    @admin.action(description='Mark selected applications as under review')
    def mark_under_review(self, request, queryset):
        queryset.update(status=Application.Status.UNDER_REVIEW)

    @admin.action(description='Mark selected applications as hired')
    def mark_hired(self, request, queryset):
        queryset.update(status=Application.Status.HIRED)

    @admin.action(description='Mark selected applications as rejected')
    def mark_rejected(self, request, queryset):
        queryset.update(status=Application.Status.REJECTED)
