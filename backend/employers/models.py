import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class EmployerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employer_profile',
    )
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employers',
    )
    full_name = models.CharField(_('full name'), max_length=255)
    designation = models.CharField(_('designation'), max_length=255, blank=True, default='')
    phone_secondary = models.CharField(_('secondary phone'), max_length=20, blank=True, default='')
    is_verified = models.BooleanField(_('verified'), default=False)
    is_company_admin = models.BooleanField(_('company admin'), default=False)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('employer profile')
        verbose_name_plural = _('employer profiles')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return f'{self.full_name} - {self.company.name if self.company else "No Company"}'
