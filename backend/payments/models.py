import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class SubscriptionPlan(models.Model):
    class BillingCycle(models.TextChoices):
        MONTHLY = 'monthly', _('Monthly')
        QUARTERLY = 'quarterly', _('Quarterly')
        YEARLY = 'yearly', _('Yearly')

    class PlanType(models.TextChoices):
        JOB_POST = 'job_post', _('Job Post')
        FEATURED_JOB = 'featured_job', _('Featured Job')
        EMPLOYER_SUBSCRIPTION = 'employer_subscription', _('Employer Subscription')
        RESUME_ACCESS = 'resume_access', _('Resume Access')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=255)
    plan_type = models.CharField(
        _('plan type'), max_length=25,
        choices=PlanType.choices,
        default=PlanType.EMPLOYER_SUBSCRIPTION,
    )
    description = models.TextField(_('description'), blank=True, default='')
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(
        _('billing cycle'), max_length=10,
        choices=BillingCycle.choices,
        default=BillingCycle.MONTHLY,
    )
    credits = models.PositiveIntegerField(_('credits'), default=0, help_text='Number of job posts or resume views')
    is_active = models.BooleanField(_('active'), default=True)
    features = models.JSONField(_('features'), default=list, blank=True)
    sort_order = models.PositiveIntegerField(_('sort order'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('subscription plan')
        verbose_name_plural = _('subscription plans')
        ordering = ['sort_order', 'price']

    def __str__(self):
        return f'{self.name} - ₹{self.price}/{self.get_billing_cycle_display()}'


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        EXPIRED = 'expired', _('Expired')
        CANCELLED = 'cancelled', _('Cancelled')
        PENDING = 'pending', _('Pending')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True,
        related_name='subscriptions',
    )
    status = models.CharField(
        _('status'), max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    credits_remaining = models.PositiveIntegerField(_('credits remaining'), default=0)
    start_date = models.DateTimeField(_('start date'), blank=True, null=True)
    end_date = models.DateTimeField(_('end date'), blank=True, null=True)
    cancelled_at = models.DateTimeField(_('cancelled at'), blank=True, null=True)
    auto_renew = models.BooleanField(_('auto renew'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.plan.name if self.plan else "No Plan"}'


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        SUCCESS = 'success', _('Success')
        FAILED = 'failed', _('Failed')
        REFUNDED = 'refunded', _('Refunded')

    class PaymentFor(models.TextChoices):
        SUBSCRIPTION = 'subscription', _('Subscription')
        JOB_POST = 'job_post', _('Job Post')
        FEATURED_JOB = 'featured_job', _('Featured Job')
        RESUME_ACCESS = 'resume_access', _('Resume Access')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='payments',
    )
    payment_for = models.CharField(
        _('payment for'), max_length=20,
        choices=PaymentFor.choices,
        default=PaymentFor.SUBSCRIPTION,
    )
    razorpay_order_id = models.CharField(_('Razorpay order ID'), max_length=255, unique=True)
    razorpay_payment_id = models.CharField(_('Razorpay payment ID'), max_length=255, blank=True, default='')
    razorpay_signature = models.TextField(_('Razorpay signature'), blank=True, default='')
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3, default='INR')
    status = models.CharField(
        _('status'), max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    payment_data = models.JSONField(_('payment data'), default=dict, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['razorpay_order_id']),
        ]

    def __str__(self):
        return f'{self.user.email} - ₹{self.amount} - {self.get_status_display()}'
