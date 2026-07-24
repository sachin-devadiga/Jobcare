from rest_framework import serializers
from .models import Notification, Device


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'notification_type', 'title', 'body', 'data', 'is_read', 'is_sent', 'created_at']
        read_only_fields = ['id', 'recipient', 'created_at']


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'user', 'fcm_token', 'platform', 'device_id', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
        extra_kwargs = {
            'fcm_token': {'validators': []},
        }

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SendNotificationSerializer(serializers.Serializer):
    recipient_id = serializers.UUIDField()
    notification_type = serializers.ChoiceField(choices=Notification.NotificationType.choices)
    title = serializers.CharField(max_length=255)
    body = serializers.CharField()
    data = serializers.JSONField(required=False, default=dict)
