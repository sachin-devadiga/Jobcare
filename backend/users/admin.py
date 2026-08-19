from django.contrib import admin

from .models import EmployeeProfile


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'city', 'availability', 'experience_years', 'profile_completion_score', 'is_profile_complete', 'updated_at')
    list_filter = ('availability', 'gender', 'is_profile_complete', 'aadhaar_verified', 'state')
    search_fields = ('full_name', 'user__email', 'user__phone', 'city', 'state', 'skills')
    ordering = ('-updated_at',)
    autocomplete_fields = ('user',)
    readonly_fields = ('profile_completion_score', 'is_profile_complete', 'created_at', 'updated_at')
    fieldsets = (
        ('Identity', {'fields': ('user', 'full_name', 'avatar', 'date_of_birth', 'gender')}),
        ('Location', {'fields': ('address', 'city', 'state', 'pincode', 'latitude', 'longitude')}),
        ('Profile data', {'fields': ('skills', 'experience_years', 'education', 'experiences', 'languages', 'certificates')}),
        ('Job preferences', {'fields': ('expected_salary', 'preferred_job_categories', 'preferred_locations', 'availability')}),
        ('Documents and verification', {'fields': ('resume_url', 'voice_resume_url', 'aadhaar_number', 'aadhaar_verified')}),
        ('Status', {'fields': ('profile_completion_score', 'is_profile_complete', 'created_at', 'updated_at')}),
    )

