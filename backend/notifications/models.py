import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        APPLICATION = 'application', _('Application Update')
        JOB = 'job', _('Job Alert')
        INTERVIEW = 'interview', _('Interview Update')
        PAYMENT = 'payment', _('Payment Update')
        SYSTEM = 'system', _('System Notification')
        GENERAL = 'general', _('General')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    notification_type = models.CharField(
        _('type'), max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
    )
    title = models.CharField(_('title'), max_length=255)
    body = models.TextField(_('body'))
    data = models.JSONField(_('data'), default=dict, blank=True)
    is_read = models.BooleanField(_('read'), default=False)
    is_sent = models.BooleanField(_('sent'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.title} -> {self.recipient.email}'


class Device(models.Model):
    class Platform(models.TextChoices):
        ANDROID = 'android', _('Android')
        IOS = 'ios', _('iOS')
        WEB = 'web', _('Web')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='devices',
    )
    fcm_token = models.TextField(_('FCM token'), unique=True)
    platform = models.CharField(
        _('platform'), max_length=10,
        choices=Platform.choices,
        default=Platform.ANDROID,
    )
    device_id = models.CharField(_('device ID'), max_length=255, blank=True, default='')
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('device')
        verbose_name_plural = _('devices')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f'{self.platform} - {self.user.email}'
