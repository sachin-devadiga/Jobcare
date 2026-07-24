import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

logger = logging.getLogger('jobcare')
User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
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
            logger.warning(f'Notification WS auth failed: {e}')
            await self.close(code=4001)
            return

        self.group_name = f'notifications_{self.user.id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connected',
            'user_id': str(self.user.id),
        }))

    async def disconnect(self, close_code):
        if self.user:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def receive(self, text_data=None, bytes_data=None):
        if not self.user:
            return
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': 'Notifications channel is read-only',
        }))

    async def notification_event(self, event):
        await self.send(text_data=json.dumps({
            'type': event.get('type', 'notification'),
            'notification': event.get('notification', {}),
            'data': event.get('data', {}),
        }))

    async def badge_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'badge_update',
            'unread_count': event.get('unread_count', 0),
        }))
