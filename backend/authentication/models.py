import uuid
import re
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email is required'))
        email = self.normalize_email(email).lower()
        if 'name' not in extra_fields or not extra_fields.get('name'):
            extra_fields['name'] = email.split('@')[0]
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('name', 'Admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        EMPLOYEE = 'employee', _('Employee')
        EMPLOYER = 'employer', _('Employer')
        ADMIN = 'admin', _('Admin')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('full name'), max_length=255, default='', blank=True)
    email = models.EmailField(_('email address'), unique=True, max_length=255, db_index=True)
    phone = models.CharField(
        _('phone number'), max_length=20, unique=True, db_index=True,
        validators=[RegexValidator(regex=r'^\+?[1-9]\d{9,14}$', message=_('Enter a valid phone number'))],
    )
    role = models.CharField(_('role'), max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    is_verified = models.BooleanField(_('verified'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'role']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'role']),
            models.Index(fields=['phone']),
            models.Index(fields=['role', 'is_active', 'is_verified']),
        ]

    def __str__(self):
        return f'{self.get_display_name()} ({self.get_role_display()})'

    def get_display_name(self):
        return self.name or self.email.split('@')[0]

    @property
    def is_employee(self):
        return self.role == self.Role.EMPLOYEE

    @property
    def is_employer(self):
        return self.role == self.Role.EMPLOYER

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN
