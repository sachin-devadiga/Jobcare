import json
import hashlib
import hmac
import logging
from decimal import Decimal
from typing import Optional, Dict, Any
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import razorpay

logger = logging.getLogger('jobcare')


class RazorpayService:
    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
        self.client = razorpay.Client(auth=(self.key_id, self.key_secret))

    def create_order(
        self,
        amount: Decimal,
        currency: str = 'INR',
        receipt: str = None,
        notes: Dict = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            paise_amount = int(amount * 100)
            order_data = {
                'amount': paise_amount,
                'currency': currency,
                'receipt': receipt or '',
                'notes': notes or {},
                'payment_capture': 1,
            }
            order = self.client.order.create(data=order_data)
            logger.info(f'Razorpay order created: {order["id"]}')
            return {
                'id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'receipt': order['receipt'],
                'status': order['status'],
                'key_id': self.key_id,
            }
        except Exception as e:
            logger.error(f'Razorpay create order error: {str(e)}', exc_info=True)
            return None

    def verify_payment(
        self,
        order_id: str,
        payment_id: str,
        signature: str,
    ) -> bool:
        try:
            expected_signature = hmac.new(
                self.key_secret.encode('utf-8'),
                f'{order_id}|{payment_id}'.encode('utf-8'),
                hashlib.sha256,
            ).hexdigest()
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f'Razorpay signature verification error: {str(e)}')
            return False

    def fetch_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            logger.error(f'Razorpay fetch payment error: {str(e)}')
            return None

    def refund_payment(
        self,
        payment_id: str,
        amount: Decimal = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            refund_data = {}
            if amount:
                refund_data['amount'] = int(amount * 100)
            refund = self.client.payment.refund(payment_id, refund_data)
            logger.info(f'Razorpay refund processed: {refund["id"]}')
            return refund
        except Exception as e:
            logger.error(f'Razorpay refund error: {str(e)}')
            return None


class PaymentService:
    def __init__(self):
        self.razorpay = RazorpayService()

    def create_payment_order(
        self,
        user,
        plan_id,
        payment_for,
    ) -> Optional[Dict]:
        from .models import SubscriptionPlan, Payment, Subscription
        from django.shortcuts import get_object_or_404

        plan = get_object_or_404(SubscriptionPlan, id=plan_id)

        receipt = f'{payment_for}_{user.id}_{timezone.now().timestamp()}'
        order = self.razorpay.create_order(
            amount=plan.price,
            receipt=receipt,
            notes={
                'user_id': str(user.id),
                'plan_id': str(plan_id),
                'payment_for': payment_for,
            },
        )

        if not order:
            return None

        payment = Payment.objects.create(
            user=user,
            payment_for=payment_for,
            razorpay_order_id=order['id'],
            amount=plan.price,
            currency='INR',
            status='pending',
            payment_data={'plan_id': str(plan_id), 'plan_name': plan.name},
        )

        return {
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'key_id': order['key_id'],
            'payment_id': str(payment.id),
            'plan': {
                'id': str(plan.id),
                'name': plan.name,
                'price': str(plan.price),
            },
        }

    def verify_and_process_payment(
        self,
        user,
        razorpay_order_id,
        razorpay_payment_id,
        razorpay_signature,
        plan_id=None,
    ) -> Optional[Dict]:
        from .models import Payment, SubscriptionPlan, Subscription

        is_valid = self.razorpay.verify_payment(
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature,
        )

        if not is_valid:
            return None

        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            return None

        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = 'success'
        payment.save()

        if plan_id:
            plan = SubscriptionPlan.objects.get(id=plan_id)
            end_date = timezone.now()
            if plan.billing_cycle == 'monthly':
                end_date += timedelta(days=30)
            elif plan.billing_cycle == 'quarterly':
                end_date += timedelta(days=90)
            elif plan.billing_cycle == 'yearly':
                end_date += timedelta(days=365)

            subscription, created = Subscription.objects.get_or_create(
                user=user,
                plan=plan,
                defaults={
                    'status': 'active',
                    'credits_remaining': plan.credits,
                    'start_date': timezone.now(),
                    'end_date': end_date,
                    'auto_renew': True,
                },
            )
            if not created:
                subscription.status = 'active'
                subscription.credits_remaining += plan.credits
                subscription.end_date = end_date
                subscription.save()

            payment.subscription = subscription
            payment.save()

            return {
                'payment_id': str(payment.id),
                'subscription_id': str(subscription.id),
                'razorpay_payment_id': razorpay_payment_id,
                'amount': str(payment.amount),
                'plan_name': plan.name,
                'credits_added': plan.credits,
                'valid_until': end_date.isoformat(),
            }

        return {
            'payment_id': str(payment.id),
            'razorpay_payment_id': razorpay_payment_id,
            'amount': str(payment.amount),
            'status': 'success',
        }
