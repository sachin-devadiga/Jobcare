from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Payment, Subscription, SubscriptionPlan


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type', 'description', 'price',
            'billing_cycle', 'credits', 'is_active', 'features',
            'sort_order', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'plan', 'plan_details', 'status',
            'credits_remaining', 'start_date', 'end_date',
            'cancelled_at', 'auto_renew', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'status', 'start_date', 'end_date',
                           'cancelled_at', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'subscription', 'payment_for',
            'razorpay_order_id', 'razorpay_payment_id',
            'razorpay_signature', 'amount', 'currency', 'status',
            'payment_data', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']


class CreateOrderSerializer(serializers.Serializer):
    plan_id = serializers.UUIDField()
    payment_for = serializers.ChoiceField(choices=Payment.PaymentFor.choices)


class VerifyPaymentSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()
    plan_id = serializers.UUIDField(required=False)


class CreateSubscriptionSerializer(serializers.Serializer):
    plan_id = serializers.UUIDField()
    auto_renew = serializers.BooleanField(default=True)
