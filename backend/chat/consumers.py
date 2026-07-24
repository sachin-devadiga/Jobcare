import json
import logging
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import Conversation, ConversationParticipant, Message

logger = logging.getLogger('jobcare')
User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = None
        token = self.scope.get('query_string', b'').decode()
        if 'token=' in token:
            token = token.split('token=')[-1].split('&')[0]

        if not token:
            await self.close(code=4001)
            return

        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            self.user = await database_sync_to_async(User.objects.get)(id=user_id)
        except (TokenError, User.DoesNotExist, Exception) as e:
            logger.warning(f'Chat WS auth failed: {e}')
            await self.close(code=4001)
            return

        self.user_group_prefix = f'user_{self.user.id}'
        self.user_group_name = f'user_{self.user.id}'

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name,
        )

        await self.accept()

        await self.broadcast_user_status(True)

        await self.send(text_data=json.dumps({
            'type': 'connected',
            'user_id': str(self.user.id),
            'message': 'Connected to chat server',
        }))

    async def disconnect(self, close_code):
        if self.user:
            await self.broadcast_user_status(False)
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name,
            )

    async def receive(self, text_data=None, bytes_data=None):
        if not self.user:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON',
            }))
            return

        handler = getattr(self, f"handle_{data.get('type', '')}", None)
        if handler:
            await handler(data)
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f"Unknown message type: {data.get('type')}",
            }))

    async def handle_send_message(self, data):
        conversation_id = data.get('conversation_id')
        content = data.get('content', '')
        message_type = data.get('message_type', 'text')
        attachment_url = data.get('attachment_url', '')

        if not conversation_id or not content.strip():
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'conversation_id and content are required',
            }))
            return

        try:
            conversation = await database_sync_to_async(
                Conversation.objects.get
            )(id=conversation_id, participants=self.user)
        except Conversation.DoesNotExist:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Conversation not found',
            }))
            return

        message = await database_sync_to_async(Message.objects.create)(
            conversation=conversation,
            sender=self.user,
            content=content.strip(),
            message_type=message_type,
            attachment_url=attachment_url,
        )

        conversation.last_message_at = message.created_at
        await database_sync_to_async(
            conversation.save
        )(update_fields=['last_message_at'])

        message_data = await self._serialize_message(message)

        participant_ids = await database_sync_to_async(
            lambda: list(conversation.participants.values_list('id', flat=True))
        )()

        for pid in participant_ids:
            await self.channel_layer.group_send(
                f'user_{pid}',
                {
                    'type': 'chat_message',
                    'event': 'new_message',
                    'data': message_data,
                },
            )

        message_data['status'] = 'sent'
        await self.send(text_data=json.dumps({
            'type': 'message_sent',
            'data': message_data,
        }))

    async def handle_mark_read(self, data):
        conversation_id = data.get('conversation_id')

        if not conversation_id:
            return

        try:
            conversation = await database_sync_to_async(
                Conversation.objects.get
            )(id=conversation_id, participants=self.user)
        except Conversation.DoesNotExist:
            return

        now = timezone.now()
        await database_sync_to_async(
            ConversationParticipant.objects.filter(
                conversation=conversation, user=self.user,
            ).update
        )(last_read_at=now)

        updated = await database_sync_to_async(
            Message.objects.filter(
                conversation=conversation,
            ).exclude(sender=self.user).filter(
                is_read=False,
            ).update
        )(is_read=True, read_at=now)

        if updated > 0:
            participant_ids = await database_sync_to_async(
                lambda: list(conversation.participants.values_list('id', flat=True))
            )()
            for pid in participant_ids:
                if str(pid) != str(self.user.id):
                    await self.channel_layer.group_send(
                        f'user_{pid}',
                        {
                            'type': 'chat_message',
                            'event': 'messages_read',
                            'data': {
                                'conversation_id': conversation_id,
                                'read_by': str(self.user.id),
                                'read_at': now.isoformat(),
                            },
                        },
                    )

    async def handle_typing_start(self, data):
        await self._broadcast_typing(data, 'typing_start')

    async def handle_typing_stop(self, data):
        await self._broadcast_typing(data, 'typing_stop')

    async def _broadcast_typing(self, data, event_type):
        conversation_id = data.get('conversation_id')
        if not conversation_id:
            return

        try:
            conversation = await database_sync_to_async(
                Conversation.objects.get
            )(id=conversation_id, participants=self.user)
        except Conversation.DoesNotExist:
            return

        participant_ids = await database_sync_to_async(
            lambda: list(conversation.participants.exclude(
                id=self.user.id
            ).values_list('id', flat=True))
        )()

        for pid in participant_ids:
            await self.channel_layer.group_send(
                f'user_{pid}',
                {
                    'type': 'chat_message',
                    'event': event_type,
                    'data': {
                        'conversation_id': conversation_id,
                        'user_id': str(self.user.id),
                        'user_name': self.user.email,
                    },
                },
            )

    async def handle_user_online(self, data):
        await self.broadcast_user_status(True)

    async def handle_user_offline(self, data):
        await self.broadcast_user_status(False)

    async def broadcast_user_status(self, is_online):
        conversation_ids = await database_sync_to_async(
            lambda: list(
                Conversation.objects.filter(
                    participants=self.user,
                ).values_list('id', flat=True)
            )
        )()

        participant_ids = await database_sync_to_async(
            lambda: list(
                ConversationParticipant.objects.filter(
                    conversation_id__in=conversation_ids,
                ).exclude(user=self.user).values_list('user_id', flat=True)
            )
        )()

        for pid in set(participant_ids):
            await self.channel_layer.group_send(
                f'user_{pid}',
                {
                    'type': 'chat_message',
                    'event': 'user_online' if is_online else 'user_offline',
                    'data': {
                        'user_id': str(self.user.id),
                        'is_online': is_online,
                    },
                },
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': event['event'],
            'data': event['data'],
        }))

    async def _serialize_message(self, message):
        return {
            'id': str(message.id),
            'conversation_id': str(message.conversation_id),
            'sender_id': str(message.sender_id),
            'content': message.content,
            'attachment_url': message.attachment_url or '',
            'message_type': message.message_type,
            'is_read': message.is_read,
            'created_at': message.created_at.isoformat(),
        }
