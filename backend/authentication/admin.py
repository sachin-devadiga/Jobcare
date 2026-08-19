from django.contrib import admin

from .models import User
from config.admin_tools import export_as_csv


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'phone', 'role', 'is_verified', 'is_staff', 'is_active', 'created_at')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_superuser', 'is_active', 'created_at')
    search_fields = ('email', 'name', 'phone')
    ordering = ('-created_at',)
    readonly_fields = ('last_login', 'created_at', 'updated_at')
    filter_horizontal = ('groups', 'user_permissions')
    actions = ('activate_users', 'block_users', 'verify_users', export_as_csv)

    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Block selected users')
    def block_users(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description='Mark selected users as verified')
    def verify_users(self, request, queryset):
        queryset.update(is_verified=True)
