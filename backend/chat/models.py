import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ConversationParticipant',
        related_name='conversations',
    )
    job = models.ForeignKey(
        'jobs.Job', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='conversations',
    )
    subject = models.CharField(_('subject'), max_length=255, blank=True, default='')
    last_message_at = models.DateTimeField(_('last message at'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('conversation')
        verbose_name_plural = _('conversations')
        ordering = ['-last_message_at', '-created_at']
        indexes = [
            models.Index(fields=['-last_message_at']),
            models.Index(fields=['job']),
        ]

    def __str__(self):
        return f'Conversation {self.id} - {self.subject or "No subject"}'


class ConversationParticipant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE,
        related_name='participant_links',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='conversation_participations',
    )
    last_read_at = models.DateTimeField(_('last read at'), blank=True, null=True)
    is_muted = models.BooleanField(_('muted'), default=False)
    joined_at = models.DateTimeField(_('joined at'), auto_now_add=True)

    class Meta:
        verbose_name = _('conversation participant')
        verbose_name_plural = _('conversation participants')
        unique_together = ['conversation', 'user']

    def __str__(self):
        return f'{self.user.email} in {self.conversation.id}'


class Message(models.Model):
    class MessageType(models.TextChoices):
        TEXT = 'text', _('Text')
        IMAGE = 'image', _('Image')
        FILE = 'file', _('File')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='sent_messages',
    )
    content = models.TextField(_('content'), blank=True, default='')
    attachment_url = models.URLField(_('attachment URL'), max_length=500, blank=True, default='')
    message_type = models.CharField(
        _('message type'), max_length=10,
        choices=MessageType.choices,
        default=MessageType.TEXT,
    )
    is_read = models.BooleanField(_('read'), default=False)
    read_at = models.DateTimeField(_('read at'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f'Message from {self.sender.email} in {self.conversation.id}'
