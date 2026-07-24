from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.db import models
from django.utils import timezone

from .models import Conversation, ConversationParticipant, Message
from .serializers import (
    ConversationListSerializer, ConversationDetailSerializer,
    ConversationCreateSerializer, MessageSerializer,
    CreateMessageSerializer, MarkAsReadSerializer,
)


@extend_schema(tags=['Chat - Conversations'])
class ConversationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ConversationListSerializer(many=True)},
        description='List user conversations',
    )
    def get(self, request):
        conversations = Conversation.objects.filter(
            participants=request.user,
        ).select_related('job').prefetch_related(
            'participant_links__user',
            'participant_links__user__employee_profile',
            'participant_links__user__employer_profile',
            'messages',
        ).order_by('-last_message_at', '-created_at')

        search = request.query_params.get('search', '')
        if search:
            conversations = conversations.filter(
                models.Q(subject__icontains=search) |
                models.Q(participants__employee_profile__full_name__icontains=search) |
                models.Q(participants__employer_profile__full_name__icontains=search) |
                models.Q(participants__email__icontains=search)
            ).distinct()

        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))
        start = (page - 1) * per_page
        end = start + per_page
        total = conversations.count()
        results = conversations[start:end]

        serializer = ConversationListSerializer(
            results, many=True, context={'request': request},
        )
        return Response({
            'success': True,
            'data': {
                'results': serializer.data,
                'count': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page,
            },
        })

    @extend_schema(
        request=ConversationCreateSerializer,
        responses={201: ConversationDetailSerializer},
        description='Create a new conversation',
    )
    def post(self, request):
        serializer = ConversationCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        conversation = serializer.save()
        result = ConversationDetailSerializer(
            conversation, context={'request': request},
        )
        return Response(
            {'success': True, 'message': 'Conversation created', 'data': result.data},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['Chat - Conversations'])
class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Conversation.objects.prefetch_related(
                'participant_links__user',
                'participant_links__user__employee_profile',
                'participant_links__user__employer_profile',
                'messages__sender',
            ).get(id=pk, participants=user)
        except Conversation.DoesNotExist:
            return None

    @extend_schema(
        responses={200: ConversationDetailSerializer},
        description='Get conversation details with messages',
    )
    def get(self, request, pk):
        conversation = self.get_object(pk, request.user)
        if not conversation:
            return Response(
                {'success': False, 'message': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        self._update_last_read(conversation, request.user)
        serializer = ConversationDetailSerializer(
            conversation, context={'request': request},
        )
        return Response({'success': True, 'data': serializer.data})

    def _update_last_read(self, conversation, user):
        ConversationParticipant.objects.filter(
            conversation=conversation, user=user,
        ).update(last_read_at=timezone.now())


@extend_schema(tags=['Chat - Messages'])
class MessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: MessageSerializer(many=True)},
        description='List messages for a conversation',
    )
    def get(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(
                id=conversation_id, participants=request.user,
            )
        except Conversation.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        messages = Message.objects.filter(
            conversation=conversation,
        ).select_related('sender').order_by('-created_at')

        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        total = messages.count()
        results = messages[offset:offset + limit]

        serializer = MessageSerializer(reversed(results), many=True)
        return Response({
            'success': True,
            'data': {
                'results': serializer.data,
                'count': total,
                'has_more': (offset + limit) < total,
            },
        })

    @extend_schema(
        request=CreateMessageSerializer,
        responses={201: MessageSerializer},
        description='Send a message in a conversation',
    )
    def post(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(
                id=conversation_id, participants=request.user,
            )
        except Conversation.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data['conversation'] = conversation_id
        serializer = CreateMessageSerializer(
            data=data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        message = serializer.save()

        conversation.last_message_at = message.created_at
        conversation.save(update_fields=['last_message_at'])

        result = MessageSerializer(message)
        return Response(
            {'success': True, 'message': 'Message sent', 'data': result.data},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['Chat - Messages'])
class MarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=MarkAsReadSerializer,
        responses={200: None},
        description='Mark conversation messages as read',
    )
    def post(self, request):
        serializer = MarkAsReadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation_id = serializer.validated_data['conversation_id']
        try:
            conversation = Conversation.objects.get(
                id=conversation_id, participants=request.user,
            )
        except Conversation.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        now = timezone.now()
        ConversationParticipant.objects.filter(
            conversation=conversation, user=request.user,
        ).update(last_read_at=now)

        Message.objects.filter(
            conversation=conversation,
        ).exclude(sender=request.user).filter(
            is_read=False,
        ).update(is_read=True, read_at=now)

        return Response(
            {'success': True, 'message': 'Messages marked as read'},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Chat - Messages'])
class UnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: None},
        description='Get total unread message count',
    )
    def get(self, request):
        conversations = Conversation.objects.filter(participants=request.user)
        total_unread = 0
        for conv in conversations:
            try:
                participant = conv.participant_links.get(user=request.user)
                if participant.last_read_at:
                    total_unread += conv.messages.exclude(sender=request.user).filter(
                        created_at__gt=participant.last_read_at
                    ).count()
                else:
                    total_unread += conv.messages.exclude(sender=request.user).count()
            except ConversationParticipant.DoesNotExist:
                pass

        return Response({
            'success': True,
            'data': {'unread_count': total_unread},
        })
