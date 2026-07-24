import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class IntakeQuestion(models.Model):
    QUESTION_KEYS = [
        ('name', _('Name')),
        ('education', _('Education')),
        ('location', _('Location')),
        ('job_interest', _('Job Interest')),
        ('experience', _('Experience')),
        ('skills', _('Skills')),
        ('salary_expectation', _('Expected Salary')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.PositiveIntegerField(_('order'), unique=True)
    question_text_en = models.TextField(_('question text (EN)'))
    question_key = models.SlugField(_('question key'), max_length=50, choices=QUESTION_KEYS)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('intake question')
        verbose_name_plural = _('intake questions')
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.question_key}"


class CallSession(models.Model):
    class Language(models.TextChoices):
        HINDI = 'hindi', _('Hindi')
        KANNADA = 'kannada', _('Kannada')
        TAMIL = 'tamil', _('Tamil')
        ENGLISH = 'english', _('English')

    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')
        ABANDONED = 'abandoned', _('Abandoned')
        FAILED = 'failed', _('Failed')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(_('phone number'), max_length=20)
    language = models.CharField(
        _('language'), 
        max_length=20, 
        choices=Language.choices, 
        default=Language.HINDI
    )
    status = models.CharField(
        _('status'), 
        max_length=20, 
        choices=Status.choices, 
        default=Status.IN_PROGRESS
    )
    current_question_index = models.PositiveIntegerField(_('current question index'), default=0)
    started_at = models.DateTimeField(_('started at'), auto_now_add=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    provider_call_sid = models.CharField(_('provider call SID'), max_length=100, unique=True)
    email = models.EmailField(_('email'), blank=True, default='')
    ai_summary = models.TextField(_('AI summary'), blank=True, default='')
    profile_data = models.JSONField(_('profile data'), blank=True, default=dict)
    pdf_file = models.FileField(_('PDF file'), upload_to='intake_pdfs/', null=True, blank=True)

    class Meta:
        verbose_name = _('call session')
        verbose_name_plural = _('call sessions')
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.phone_number} - {self.status}"


class CallAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        CallSession, 
        on_delete=models.CASCADE, 
        related_name='answers'
    )
    question = models.ForeignKey(
        IntakeQuestion, 
        on_delete=models.PROTECT,
        related_name='answers'
    )
    answer_text = models.TextField(_('answer text'))
    confirmed = models.BooleanField(_('confirmed'), default=False)
    audio_recording_url = models.URLField(_('audio recording URL'), max_length=500, null=True, blank=True)
    answered_at = models.DateTimeField(_('answered at'), auto_now_add=True)

    class Meta:
        verbose_name = _('call answer')
        verbose_name_plural = _('call answers')
        ordering = ['answered_at']

    def __str__(self):
        return f"{self.session.phone_number} - {self.question.question_key}"
