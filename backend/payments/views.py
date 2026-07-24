from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

from authentication.permissions import IsEmployer
from .models import Payment, Subscription, SubscriptionPlan
from .serializers import (
    PaymentSerializer, SubscriptionSerializer, SubscriptionPlanSerializer,
    CreateOrderSerializer, VerifyPaymentSerializer, CreateSubscriptionSerializer,
)
from .services import PaymentService, RazorpayService

payment_service = PaymentService()
razorpay_service = RazorpayService()


@extend_schema(tags=['Payments'])
class SubscriptionPlanListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: SubscriptionPlanSerializer(many=True)},
        description='List all active subscription plans',
    )
    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order', 'price')
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


@extend_schema(tags=['Payments'])
class CreatePaymentOrderView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    @extend_schema(
        request=CreateOrderSerializer,
        responses={200: OpenApiResponse(description='Payment order created')},
        description='Create a Razorpay payment order',
    )
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = payment_service.create_payment_order(
            user=request.user,
            plan_id=serializer.validated_data['plan_id'],
            payment_for=serializer.validated_data['payment_for'],
        )

        if not result:
            return Response(
                {'success': False, 'message': 'Failed to create payment order'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {'success': True, 'message': 'Payment order created', 'data': result},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Payments'])
class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    @extend_schema(
        request=VerifyPaymentSerializer,
        responses={200: OpenApiResponse(description='Payment verified')},
        description='Verify Razorpay payment',
    )
    def post(self, request):
        serializer = VerifyPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = payment_service.verify_and_process_payment(
            user=request.user,
            razorpay_order_id=serializer.validated_data['razorpay_order_id'],
            razorpay_payment_id=serializer.validated_data['razorpay_payment_id'],
            razorpay_signature=serializer.validated_data['razorpay_signature'],
            plan_id=serializer.validated_data.get('plan_id'),
        )

        if not result:
            return Response(
                {'success': False, 'message': 'Payment verification failed'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {'success': True, 'message': 'Payment verified successfully', 'data': result},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Payments'])
class PaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: PaymentSerializer(many=True)},
        description='Get payment history',
    )
    def get(self, request):
        payments = Payment.objects.filter(user=request.user).order_by('-created_at')
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))
        paginator = __import__('django.core.paginator', fromlist=['Paginator']).Paginator(payments, per_page)
        page_obj = paginator.get_page(page)
        serializer = PaymentSerializer(page_obj.object_list, many=True)
        return Response(
            {
                'success': True,
                'data': {
                    'results': serializer.data,
                    'count': paginator.count,
                    'page': page,
                    'total_pages': paginator.num_pages,
                },
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Payments'])
class MySubscriptionsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: SubscriptionSerializer(many=True)},
        description='Get my subscriptions',
    )
    def get(self, request):
        subscriptions = Subscription.objects.filter(user=request.user).order_by('-created_at')
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


@extend_schema(tags=['Payments'])
class CreateSubscriptionView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    @extend_schema(
        request=CreateSubscriptionSerializer,
        responses={201: SubscriptionSerializer},
        description='Create a new subscription',
    )
    def post(self, request):
        serializer = CreateSubscriptionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        plan = SubscriptionPlan.objects.filter(
            id=serializer.validated_data['plan_id'],
            is_active=True,
        ).first()

        if not plan:
            return Response(
                {'success': False, 'message': 'Invalid or inactive plan'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            status='pending',
            auto_renew=serializer.validated_data['auto_renew'],
        )

        result_serializer = SubscriptionSerializer(subscription)
        return Response(
            {'success': True, 'message': 'Subscription created', 'data': result_serializer.data},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['Payments'])
class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiResponse(description='Subscription cancelled')},
        description='Cancel a subscription',
    )
    def post(self, request, pk):
        try:
            subscription = Subscription.objects.get(id=pk, user=request.user)
        except Subscription.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Subscription not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        subscription.status = 'cancelled'
        subscription.cancelled_at = __import__('django.utils.timezone', fromlist=['now']).now()
        subscription.auto_renew = False
        subscription.save()

        return Response(
            {'success': True, 'message': 'Subscription cancelled'},
            status=status.HTTP_200_OK,
        )
