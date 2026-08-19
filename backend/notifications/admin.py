from django.contrib import admin

from .models import Device, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'is_read', 'is_sent', 'created_at')
    list_filter = ('notification_type', 'is_read', 'is_sent', 'created_at')
    search_fields = ('title', 'body', 'recipient__email', 'recipient__name')
    ordering = ('-created_at',)
    autocomplete_fields = ('recipient',)
    readonly_fields = ('created_at',)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'device_id', 'is_active', 'updated_at')
    list_filter = ('platform', 'is_active')
    search_fields = ('user__email', 'user__name', 'device_id', 'fcm_token')
    ordering = ('-updated_at',)
    autocomplete_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')

