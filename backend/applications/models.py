import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = 'applied', _('Applied')
        UNDER_REVIEW = 'under_review', _('Under Review')
        SHORTLISTED = 'shortlisted', _('Shortlisted')
        INTERVIEW_SCHEDULED = 'interview_scheduled', _('Interview Scheduled')
        SELECTED = 'selected', _('Selected')
        OFFERED = 'offered', _('Offered')
        HIRED = 'hired', _('Hired')
        REJECTED = 'rejected', _('Rejected')
        WITHDRAWN = 'withdrawn', _('Withdrawn')

    class InterviewType(models.TextChoices):
        IN_PERSON = 'in_person', _('In Person')
        VIDEO = 'video', _('Video')
        CALL = 'call', _('Call')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(
        'jobs.Job', on_delete=models.CASCADE,
        related_name='applications',
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='job_applications',
    )
    status = models.CharField(
        _('status'), max_length=20,
        choices=Status.choices,
        default=Status.APPLIED,
        db_index=True,
    )

    cover_letter = models.TextField(_('cover letter'), blank=True, default='')
    resume_url = models.URLField(_('resume URL'), max_length=500, blank=True, default='')
    voice_resume_url = models.URLField(_('voice resume URL'), max_length=500, blank=True, default='')

    ai_match_score = models.FloatField(_('AI match score'), blank=True, null=True)
    employer_notes = models.TextField(_('employer notes'), blank=True, default='')
    rejection_reason = models.CharField(_('rejection reason'), max_length=500, blank=True, default='')

    interview_date = models.DateField(_('interview date'), blank=True, null=True)
    interview_time = models.TimeField(_('interview time'), blank=True, null=True)
    interview_location = models.CharField(_('interview location'), max_length=500, blank=True, default='')
    interview_type = models.CharField(
        _('interview type'), max_length=20,
        choices=InterviewType.choices,
        blank=True, null=True,
    )

    offer_letter_url = models.URLField(_('offer letter URL'), max_length=500, blank=True, default='')
    joined_date = models.DateField(_('joined date'), blank=True, null=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('application')
        verbose_name_plural = _('applications')
        ordering = ['-created_at']
        unique_together = ['job', 'employee']
        indexes = [
            models.Index(fields=['job', 'status']),
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['ai_match_score']),
        ]

    def __str__(self):
        return f'{self.employee.email} -> {self.job.title} ({self.get_status_display()})'
