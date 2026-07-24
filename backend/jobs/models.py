import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils import timezone


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=255, unique=True, db_index=True)
    slug = models.SlugField(_('slug'), max_length=255, unique=True, blank=True)
    icon = models.CharField(_('icon'), max_length=100, blank=True, default='')
    description = models.TextField(_('description'), blank=True, default='')
    is_active = models.BooleanField(_('active'), default=True)
    sort_order = models.PositiveIntegerField(_('sort order'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Skill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=255, unique=True, db_index=True)
    slug = models.SlugField(_('slug'), max_length=255, unique=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='skills',
    )
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('skill')
        verbose_name_plural = _('skills')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=255, db_index=True)
    state = models.CharField(_('state'), max_length=255, db_index=True)
    latitude = models.DecimalField(_('latitude'), max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(_('longitude'), max_digits=9, decimal_places=6, blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('city')
        verbose_name_plural = _('cities')
        ordering = ['name']
        unique_together = ['name', 'state']

    def __str__(self):
        return f'{self.name}, {self.state}'


class Job(models.Model):
    class JobType(models.TextChoices):
        FULL_TIME = 'full_time', _('Full Time')
        PART_TIME = 'part_time', _('Part Time')
        CONTRACT = 'contract', _('Contract')
        INTERNSHIP = 'internship', _('Internship')
        REMOTE = 'remote', _('Remote')

    class ShiftTiming(models.TextChoices):
        DAY = 'day', _('Day')
        NIGHT = 'night', _('Night')
        FLEXIBLE = 'flexible', _('Flexible')

    class SalaryType(models.TextChoices):
        MONTHLY = 'monthly', _('Monthly')
        YEARLY = 'yearly', _('Yearly')
        HOURLY = 'hourly', _('Hourly')

    class Urgency(models.TextChoices):
        HIGH = 'high', _('High')
        MEDIUM = 'medium', _('Medium')
        LOW = 'low', _('Low')

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        PAUSED = 'paused', _('Paused')
        CLOSED = 'closed', _('Closed')
        FILLED = 'filled', _('Filled')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.Company', on_delete=models.CASCADE,
        related_name='jobs',
    )
    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='posted_jobs',
    )
    title = models.CharField(_('title'), max_length=255, db_index=True)
    slug = models.SlugField(_('slug'), max_length=255, unique=True, blank=True)
    description = models.TextField(_('description'))
    responsibilities = models.JSONField(_('responsibilities'), default=list, blank=True)
    requirements = models.JSONField(_('requirements'), default=list, blank=True)

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='jobs',
    )
    skills_required = models.JSONField(_('skills required'), default=list, blank=True)
    experience_min = models.PositiveIntegerField(_('min experience'), default=0)
    experience_max = models.PositiveIntegerField(_('max experience'), default=0)
    salary_min = models.DecimalField(_('min salary'), max_digits=12, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(_('max salary'), max_digits=12, decimal_places=2, blank=True, null=True)
    salary_type = models.CharField(
        _('salary type'), max_length=10,
        choices=SalaryType.choices,
        default=SalaryType.MONTHLY,
    )

    location = models.CharField(_('location'), max_length=255, blank=True, default='')
    city = models.CharField(_('city'), max_length=100, db_index=True, blank=True, default='')
    state = models.CharField(_('state'), max_length=100, blank=True, default='')
    latitude = models.DecimalField(_('latitude'), max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(_('longitude'), max_digits=9, decimal_places=6, blank=True, null=True)

    job_type = models.CharField(
        _('job type'), max_length=20,
        choices=JobType.choices,
        default=JobType.FULL_TIME,
        db_index=True,
    )
    shift_timing = models.CharField(
        _('shift timing'), max_length=10,
        choices=ShiftTiming.choices,
        default=ShiftTiming.DAY,
    )
    education_required = models.JSONField(_('education required'), default=list, blank=True)
    benefits = models.JSONField(_('benefits'), default=list, blank=True)

    openings = models.PositiveIntegerField(_('openings'), default=1)
    urgency = models.CharField(
        _('urgency'), max_length=10,
        choices=Urgency.choices,
        default=Urgency.MEDIUM,
    )

    status = models.CharField(
        _('status'), max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    is_featured = models.BooleanField(_('featured'), default=False)
    is_urgent = models.BooleanField(_('urgent'), default=False)

    views_count = models.PositiveIntegerField(_('views count'), default=0)
    application_count = models.PositiveIntegerField(_('application count'), default=0)
    save_count = models.PositiveIntegerField(_('save count'), default=0)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    expires_at = models.DateTimeField(_('expires at'), blank=True, null=True)

    class Meta:
        verbose_name = _('job')
        verbose_name_plural = _('jobs')
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['status', 'job_type', 'city']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['experience_min', 'experience_max']),
            models.Index(fields=['salary_min', 'salary_max']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return f'{self.title} at {self.company.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f'{self.title}-{self.company.name}')
            self.slug = base_slug
            counter = 1
            while Job.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f'{base_slug}-{counter}'
                counter += 1
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)
