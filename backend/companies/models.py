import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class Company(models.Model):
    class Industry(models.TextChoices):
        TECHNOLOGY = 'technology', _('Technology')
        HEALTHCARE = 'healthcare', _('Healthcare')
        FINANCE = 'finance', _('Finance')
        EDUCATION = 'education', _('Education')
        MANUFACTURING = 'manufacturing', _('Manufacturing')
        RETAIL = 'retail', _('Retail')
        CONSTRUCTION = 'construction', _('Construction')
        HOSPITALITY = 'hospitality', _('Hospitality')
        TRANSPORTATION = 'transportation', _('Transportation')
        MEDIA = 'media', _('Media')
        AGRICULTURE = 'agriculture', _('Agriculture')
        ENERGY = 'energy', _('Energy')
        OTHER = 'other', _('Other')

    class Size(models.TextChoices):
        STARTUP = '1-10', _('1-10 employees')
        SMALL = '11-50', _('11-50 employees')
        MEDIUM = '51-200', _('51-200 employees')
        LARGE = '201-1000', _('201-1000 employees')
        ENTERPRISE = '1000+', _('1000+ employees')

    class VerificationStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        VERIFIED = 'verified', _('Verified')
        REJECTED = 'rejected', _('Rejected')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('company name'), max_length=255, unique=True, db_index=True)
    slug = models.SlugField(_('slug'), max_length=255, unique=True, blank=True)
    logo = models.ImageField(_('logo'), upload_to='company/logos/', blank=True, null=True)
    banner_image = models.ImageField(_('banner image'), upload_to='company/banners/', blank=True, null=True)
    images = models.JSONField(_('images'), default=list, blank=True)
    description = models.TextField(_('description'), blank=True, default='')
    website = models.URLField(_('website'), max_length=500, blank=True, default='')
    industry = models.CharField(_('industry'), max_length=50, choices=Industry.choices, blank=True, null=True)
    company_size = models.CharField(_('company size'), max_length=10, choices=Size.choices, blank=True, null=True)
    founded_year = models.PositiveIntegerField(_('founded year'), blank=True, null=True)
    headquarters = models.CharField(_('headquarters'), max_length=255, blank=True, default='')
    locations = models.JSONField(_('locations'), default=list, blank=True)
    verification_status = models.CharField(
        _('verification status'), max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    verification_document = models.FileField(
        _('verification document'), upload_to='company/verification/', blank=True, null=True,
    )
    is_featured = models.BooleanField(_('featured'), default=False)
    social_links = models.JSONField(_('social links'), default=dict, blank=True)
    contact_email = models.EmailField(_('contact email'), max_length=255, blank=True, default='')
    contact_phone = models.CharField(_('contact phone'), max_length=20, blank=True, default='')

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name', 'industry']),
            models.Index(fields=['verification_status']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original = self.slug
            counter = 1
            while Company.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f'{original}-{counter}'
                counter += 1
        super().save(*args, **kwargs)
