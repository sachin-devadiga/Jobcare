from django.contrib import admin

from .models import EmployerProfile


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'company', 'designation', 'is_verified', 'is_company_admin', 'updated_at')
    list_filter = ('is_verified', 'is_company_admin')
    search_fields = ('full_name', 'user__email', 'company__name', 'designation')
    ordering = ('-updated_at',)
    autocomplete_fields = ('user', 'company')
    readonly_fields = ('created_at', 'updated_at')

