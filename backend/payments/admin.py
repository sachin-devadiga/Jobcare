from django.contrib import admin

from .models import Payment, Subscription, SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'billing_cycle', 'credits', 'is_active', 'sort_order')
    list_filter = ('plan_type', 'billing_cycle', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('sort_order', 'price')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'credits_remaining', 'auto_renew', 'end_date', 'created_at')
    list_filter = ('status', 'auto_renew', 'created_at')
    search_fields = ('user__email', 'user__name', 'plan__name')
    ordering = ('-created_at',)
    autocomplete_fields = ('user', 'plan')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('razorpay_order_id', 'user', 'payment_for', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('payment_for', 'status', 'currency', 'created_at')
    search_fields = ('razorpay_order_id', 'razorpay_payment_id', 'user__email', 'user__name')
    ordering = ('-created_at',)
    autocomplete_fields = ('user', 'subscription')
    readonly_fields = ('created_at', 'updated_at')

