from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Conversation, ConversationParticipant, Message


class ConversationParticipantSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_avatar = serializers.SerializerMethodField()

    class Meta:
        model = ConversationParticipant
        fields = ['id', 'user', 'user_name', 'user_email', 'user_avatar', 'last_read_at', 'is_muted', 'joined_at']
        read_only_fields = ['id', 'joined_at']

    def get_user_name(self, obj):
        profile = getattr(obj.user, 'employee_profile', None) or getattr(obj.user, 'employer_profile', None)
        return getattr(profile, 'full_name', None) or obj.user.email

    def get_user_avatar(self, obj):
        profile = getattr(obj.user, 'employee_profile', None) or getattr(obj.user, 'employer_profile', None)
        return getattr(profile, 'avatar_url', None) or getattr(profile, 'profile_image', None) or None


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_name', 'sender_avatar',
            'content', 'attachment_url', 'message_type',
            'is_read', 'read_at', 'created_at',
        ]
        read_only_fields = ['id', 'sender', 'is_read', 'read_at', 'created_at']

    def get_sender_name(self, obj):
        profile = getattr(obj.sender, 'employee_profile', None) or getattr(obj.sender, 'employer_profile', None)
        return getattr(profile, 'full_name', None) or obj.sender.email

    def get_sender_avatar(self, obj):
        profile = getattr(obj.sender, 'employee_profile', None) or getattr(obj.sender, 'employer_profile', None)
        return getattr(profile, 'avatar_url', None) or getattr(profile, 'profile_image', None) or None


class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['conversation', 'content', 'attachment_url', 'message_type']

    def validate_conversation(self, value):
        request = self.context.get('request')
        if request and not value.participants.filter(id=request.user.id).exists():
            raise serializers.ValidationError(_('You are not a participant in this conversation'))
        return value

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class ConversationListSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'job', 'subject', 'last_message_at',
            'last_message', 'unread_count', 'other_participant',
            'is_online', 'created_at', 'updated_at',
        ]

    def get_last_message(self, obj):
        message = obj.messages.order_by('-created_at').first()
        if message:
            return MessageSerializer(message).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request:
            return 0
        try:
            participant = obj.participant_links.get(user=request.user)
            if not participant.last_read_at:
                return obj.messages.exclude(sender=request.user).count()
            return obj.messages.exclude(sender=request.user).filter(
                created_at__gt=participant.last_read_at
            ).count()
        except ConversationParticipant.DoesNotExist:
            return 0

    def get_other_participant(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        other = obj.participants.exclude(id=request.user.id).first()
        if not other:
            return None
        profile = getattr(other, 'employee_profile', None) or getattr(other, 'employer_profile', None)
        role = 'employee' if hasattr(other, 'employee_profile') and other.employee_profile else 'employer'
        return {
            'id': str(other.id),
            'name': getattr(profile, 'full_name', None) or other.email,
            'email': other.email,
            'avatar': getattr(profile, 'avatar_url', None) or getattr(profile, 'profile_image', None) or None,
            'role': role,
        }

    def get_is_online(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        other = obj.participants.exclude(id=request.user.id).first()
        if not other:
            return False
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(minutes=5)
        return hasattr(other, 'last_online') and other.last_online and other.last_online > cutoff


class ConversationDetailSerializer(serializers.ModelSerializer):
    participants = ConversationParticipantSerializer(source='participant_links', many=True, read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'job', 'subject', 'participants',
            'messages', 'last_message_at', 'created_at', 'updated_at',
        ]

    def get_messages(self, obj):
        request = self.context.get('request')
        limit = int(request.query_params.get('limit', 50)) if request else 50
        offset = int(request.query_params.get('offset', 0)) if request else 0
        messages = obj.messages.select_related('sender').order_by('-created_at')[offset:offset + limit]
        return MessageSerializer(reversed(messages), many=True).data


class ConversationCreateSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True,
    )

    class Meta:
        model = Conversation
        fields = ['job', 'subject', 'participant_ids']

    def validate_participant_ids(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(id__in=value)
        if len(users) != len(value):
            raise serializers.ValidationError(_('One or more participants not found'))
        request = self.context.get('request')
        if request and request.user.id not in value:
            value.append(request.user.id)
        return value

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create(**validated_data)
        for uid in participant_ids:
            ConversationParticipant.objects.create(
                conversation=conversation,
                user_id=uid,
            )
        return conversation


class MarkAsReadSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField()
    last_read_message_id = serializers.UUIDField(required=False)
