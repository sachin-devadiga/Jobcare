from django.contrib import admin

from .models import Company
from config.admin_tools import export_as_csv


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'company_size', 'headquarters', 'verification_status', 'is_featured', 'created_at')
    list_filter = ('industry', 'company_size', 'verification_status', 'is_featured')
    search_fields = ('name', 'headquarters', 'contact_email', 'contact_phone', 'website')
    ordering = ('-created_at',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    actions = ('verify_companies', 'reject_companies', export_as_csv)

    @admin.action(description='Verify selected companies')
    def verify_companies(self, request, queryset):
        queryset.update(verification_status=Company.VerificationStatus.VERIFIED)

    @admin.action(description='Reject selected companies')
    def reject_companies(self, request, queryset):
        queryset.update(verification_status=Company.VerificationStatus.REJECTED)
