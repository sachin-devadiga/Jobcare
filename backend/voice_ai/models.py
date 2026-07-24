import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class VoiceSession(models.Model):
    class SessionType(models.TextChoices):
        SPEECH_TO_TEXT = 'speech_to_text', _('Speech to Text')
        TEXT_TO_SPEECH = 'text_to_speech', _('Text to Speech')
        VOICE_SEARCH = 'voice_search', _('Voice Search')
        VOICE_NAVIGATION = 'voice_navigation', _('Voice Navigation')

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='voice_sessions',
    )
    session_type = models.CharField(
        _('session type'), max_length=20,
        choices=SessionType.choices,
        default=SessionType.VOICE_SEARCH,
    )
    status = models.CharField(
        _('status'), max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    audio_input = models.FileField(
        _('audio input'), upload_to='voice/input/', blank=True, null=True,
    )
    audio_url = models.URLField(_('audio URL'), max_length=500, blank=True, default='')
    input_text = models.TextField(_('input text'), blank=True, default='')
    output_text = models.TextField(_('output text'), blank=True, default='')
    output_audio_url = models.URLField(_('output audio URL'), max_length=500, blank=True, default='')
    detected_language = models.CharField(_('detected language'), max_length=20, blank=True, default='')
    confidence_score = models.FloatField(_('confidence score'), blank=True, null=True)
    processing_time_ms = models.PositiveIntegerField(_('processing time ms'), blank=True, null=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    error_message = models.TextField(_('error message'), blank=True, default='')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('voice session')
        verbose_name_plural = _('voice sessions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'session_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'{self.get_session_type_display()} - {self.id}'
