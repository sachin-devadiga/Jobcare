import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class EmployeeProfile(models.Model):
    class Availability(models.TextChoices):
        IMMEDIATE = 'immediate', _('Immediate')
        NOTICE_PERIOD = 'notice_period', _('Notice Period')
        NOT_AVAILABLE = 'not_available', _('Not Available')

    class Gender(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHER = 'other', _('Other')
        PREFER_NOT_TO_SAY = 'prefer_not_to_say', _('Prefer Not to Say')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
    )

    full_name = models.CharField(_('full name'), max_length=255)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    gender = models.CharField(_('gender'), max_length=20, choices=Gender.choices, blank=True, null=True)
    address = models.TextField(_('address'), blank=True, default='')
    city = models.CharField(_('city'), max_length=100, db_index=True, blank=True, default='')
    state = models.CharField(_('state'), max_length=100, blank=True, default='')
    pincode = models.CharField(_('pincode'), max_length=10, blank=True, default='')
    latitude = models.DecimalField(_('latitude'), max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(_('longitude'), max_digits=9, decimal_places=6, blank=True, null=True)

    skills = models.JSONField(_('skills'), default=list, blank=True)
    experience_years = models.DecimalField(_('experience years'), max_digits=4, decimal_places=1, default=0)
    education = models.JSONField(_('education'), default=list, blank=True)
    experiences = models.JSONField(_('work experience'), default=list, blank=True)
    languages = models.JSONField(_('languages'), default=list, blank=True)
    certificates = models.JSONField(_('certificates'), default=list, blank=True)

    resume_url = models.URLField(_('resume URL'), max_length=500, blank=True, default='')
    voice_resume_url = models.URLField(_('voice resume URL'), max_length=500, blank=True, default='')
    expected_salary = models.DecimalField(_('expected salary'), max_digits=12, decimal_places=2, blank=True, null=True)
    preferred_job_categories = models.JSONField(_('preferred job categories'), default=list, blank=True)
    preferred_locations = models.JSONField(_('preferred locations'), default=list, blank=True)

    availability = models.CharField(
        _('availability'), max_length=20,
        choices=Availability.choices,
        default=Availability.NOT_AVAILABLE,
    )
    aadhaar_number = models.CharField(_('aadhaar number'), max_length=12, blank=True, default='')
    aadhaar_verified = models.BooleanField(_('aadhaar verified'), default=False)

    profile_completion_score = models.FloatField(_('profile completion score'), default=0.0)
    is_profile_complete = models.BooleanField(_('profile complete'), default=False)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('employee profile')
        verbose_name_plural = _('employee profiles')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'availability']),
            models.Index(fields=['experience_years']),
        ]

    def __str__(self):
        return self.full_name or str(self.user.email)

    def calculate_completion_score(self):
        fields_weight = {
            'full_name': 5.0,
            'avatar': 5.0,
            'date_of_birth': 3.0,
            'gender': 2.0,
            'address': 3.0,
            'city': 5.0,
            'state': 3.0,
            'pincode': 3.0,
            'latitude': 2.0,
            'longitude': 2.0,
            'skills': 10.0,
            'experience_years': 10.0,
            'education': 10.0,
            'languages': 5.0,
            'certificates': 5.0,
            'resume_url': 10.0,
            'voice_resume_url': 5.0,
            'expected_salary': 5.0,
            'preferred_job_categories': 5.0,
            'preferred_locations': 3.0,
            'availability': 2.0,
        }

        score = 0.0
        total_weight = sum(fields_weight.values())

        for field, weight in fields_weight.items():
            value = getattr(self, field, None)
            if value is not None and value != '' and value != [] and value != {} and value != 0 and value != 0.0:
                score += weight

        if self.aadhaar_verified:
            score += 5.0
            total_weight += 5.0

        self.profile_completion_score = round((score / total_weight) * 100, 2)
        self.is_profile_complete = self.profile_completion_score >= 80.0
        return self.profile_completion_score

    def save(self, *args, **kwargs):
        self.calculate_completion_score()
        super().save(*args, **kwargs)
