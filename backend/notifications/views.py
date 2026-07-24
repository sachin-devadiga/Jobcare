from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from authentication.permissions import IsAdmin
from .models import Notification, Device
from .serializers import NotificationSerializer, DeviceSerializer, SendNotificationSerializer
from .repositories.notification_repository import NotificationRepository, DeviceRepository
from .services import NotificationService, FCMNotificationService, EmailNotificationService

notification_repo = NotificationRepository()
device_repo = DeviceRepository()
notification_service = NotificationService()


@extend_schema(tags=['Notifications'])
class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: NotificationSerializer(many=True)},
        description='Get my notifications',
    )
    def get(self, request):
        notifications = notification_repo.get_by_user(request.user.id)
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))
        result = notification_repo.paginate(notifications, page=page, per_page=per_page)
        serializer = NotificationSerializer(result['results'], many=True)
        result['results'] = serializer.data
        return Response({'success': True, 'data': result}, status=status.HTTP_200_OK)


@extend_schema(tags=['Notifications'])
class UnreadNotificationCountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiResponse(description='Unread count')},
        description='Get unread notification count',
    )
    def get(self, request):
        count = notification_repo.count_unread(request.user.id)
        return Response(
            {'success': True, 'data': {'unread_count': count}},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Notifications'])
class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiResponse(description='Marked as read')},
        description='Mark a notification as read',
    )
    def post(self, request, pk):
        notification = notification_repo.get_by_id(pk)
        if not notification:
            return Response(
                {'success': False, 'message': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if notification.recipient != request.user and not request.user.is_admin_user:
            return Response(
                {'success': False, 'message': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN,
            )
        notification_repo.mark_as_read(pk)
        return Response(
            {'success': True, 'message': 'Notification marked as read'},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Notifications'])
class MarkAllNotificationsReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiResponse(description='All marked as read')},
        description='Mark all notifications as read',
    )
    def post(self, request):
        notification_repo.mark_all_as_read(request.user.id)
        return Response(
            {'success': True, 'message': 'All notifications marked as read'},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Notifications'])
class DeviceRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=DeviceSerializer,
        responses={201: DeviceSerializer},
        description='Register device for push notifications',
    )
    def post(self, request):
        serializer = DeviceSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        existing = device_repo.get_by_fcm_token(serializer.validated_data['fcm_token'])
        if existing:
            if existing.user != request.user:
                existing.user = request.user
                existing.save(update_fields=['user'])
            existing.is_active = True
            existing.save(update_fields=['is_active'])
            result = DeviceSerializer(existing)
            return Response(
                {'success': True, 'message': 'Device updated', 'data': result.data},
                status=status.HTTP_200_OK,
            )
        serializer.save()
        return Response(
            {'success': True, 'message': 'Device registered', 'data': serializer.data},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        responses={200: DeviceSerializer(many=True)},
        description='Get my registered devices',
    )
    def get(self, request):
        devices = device_repo.get_by_user(request.user.id)
        serializer = DeviceSerializer(devices, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


@extend_schema(tags=['Notifications'])
class SendNotificationAdminView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        request=SendNotificationSerializer,
        responses={200: OpenApiResponse(description='Notification sent')},
        description='Send notification to a user (admin)',
    )
    def post(self, request):
        serializer = SendNotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        notification = notification_service.send_and_notify(
            recipient_id=serializer.validated_data['recipient_id'],
            notification_type=serializer.validated_data['notification_type'],
            title=serializer.validated_data['title'],
            body=serializer.validated_data['body'],
            data=serializer.validated_data.get('data', {}),
        )
        result = NotificationSerializer(notification)
        return Response(
            {'success': True, 'message': 'Notification sent', 'data': result.data},
            status=status.HTTP_200_OK,
        )
