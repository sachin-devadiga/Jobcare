import json
import uuid
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from rest_framework import status

from chat.models import Conversation, ConversationParticipant, Message
from chat.consumers import ChatConsumer
from config.asgi import application

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestChatAPI:
    def test_create_conversation(self, auth_client, employer_user):
        payload = {
            'participant_ids': [str(employer_user.id)],
            'subject': 'Job Inquiry',
        }
        response = auth_client.post('/api/v1/chat/conversations/', payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['subject'] == 'Job Inquiry'

    def test_create_conversation_without_participants(self, auth_client):
        payload = {'subject': 'Test'}
        response = auth_client.post('/api/v1/chat/conversations/', payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_conversation_invalid_participant(self, auth_client):
        payload = {
            'participant_ids': [str(uuid.uuid4())],
            'subject': 'Test',
        }
        response = auth_client.post('/api/v1/chat/conversations/', payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_conversations(self, auth_client, employee_user, employer_user):
        conv = Conversation.objects.create(subject='Test')
        ConversationParticipant.objects.create(conversation=conv, user_id=employee_user.id)
        ConversationParticipant.objects.create(conversation=conv, user=employer_user)

        response = auth_client.get('/api/v1/chat/conversations/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['count'] >= 1

    def test_list_conversations_empty(self, auth_client):
        response = auth_client.get('/api/v1/chat/conversations/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['data']['count'] == 0

    def test_list_conversations_pagination(self, auth_client, employee_user, employer_user):
        for i in range(5):
            conv = Conversation.objects.create(subject=f'Test {i}')
            ConversationParticipant.objects.create(conversation=conv, user_id=employee_user.id)
            ConversationParticipant.objects.create(conversation=conv, user=employer_user)

        response = auth_client.get('/api/v1/chat/conversations/?per_page=2')
        data = response.json()
        assert len(data['data']['results']) == 2
        assert data['data']['total_pages'] >= 3

    def test_list_conversations_search(self, auth_client, employee_user, employer_user):
        conv = Conversation.objects.create(subject='React Developer Position')
        ConversationParticipant.objects.create(conversation=conv, user_id=employee_user.id)
        ConversationParticipant.objects.create(conversation=conv, user=employer_user)

        response = auth_client.get('/api/v1/chat/conversations/?search=React')
        data = response.json()
        assert data['data']['count'] >= 1

    def test_send_message(self, auth_client, employee_user, employer_user):
        conv = Conversation.objects.create(subject='Test')
        ConversationParticipant.objects.create(conversation=conv, user_id=employee_user.id)
        ConversationParticipant.objects.create(conversation=conv, user=employer_user)

        payload = {'content': 'Hello, is this job still available?'}
        response = auth_client.post(f'/api/v1/chat/conversations/{conv.id}/messages/', payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['success'] is True
        assert data['data']['content'] == 'Hello, is this job still available?'
        assert data['data']['sender_name'] is not None

    def test_send_message_invalid_conversation(self, auth_client):
        payload = {'content': 'Hello'}
        response = auth_client.post(
            f'/api/v1/chat/conversations/{uuid.uuid4()}/messages/',
            payload,
            format='json',
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_send_message_empty_content(self, auth_client, employee_user, employer_user):
        conv = Conversation.objects.create(subject='Test')
        ConversationParticipant.objects.create(conversation=conv, user_id=employee_user.id)
        ConversationParticipant.objects.create(conversation=conv, user=employer_user)

        payload = {'content': ''}
        response = auth_client.post(f'/api/v1/chat/conversations/{conv.id}/messages/', payload, format='json')
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST)

    def test_send_message_with_attachment(self, auth_client, employee_user, employer_user):
        conv = Conversation.objects.create(subject='Test')
        ConversationParticipant.objects.create(conversation=conv, user_id=employee_user.id)
        ConversationParticipant.objects.create(conversation=conv, user=employer_user)

        payload = {
            'content': 'Here is my resume',
            'attachment_url': 'https://storage.example.com/resume.pdf',
            'message_type': 'file',
        }
        response = auth_client.post(f'/api/v1/chat/conversations/{conv.id}/messages/', payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['data']['message_type'] == 'file'

    def test_list_messages(self, auth_client, employee_user, employer_user):
        conv = Conversation.objects.create(subject='Test')
        ConversationParticipant.objects.create(conversation=conv, user_id=employee_user.id)
        ConversationParticipant.objects.create(conversation=conv, user=employer_user)
        Message.objects.create(conversation=conv, sender_id=employee_user.id, content='Hi')
        Message.objects.create(conversation=conv, sender=employer_user, content='Hello')

        response = auth_client.get(f'/api/v1/chat/conversations/{conv.id}/messages/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['data']['count'] == 2

    def test_list_messages_pagination(self, auth_client, employee_user, employer_user):
        conv = Conversation.objects.create(subject='Test')
        ConversationParticipant.objects.create(conversation=conv, user_id=employee_user.id)
        ConversationParticipant.objects.create(conversation=conv, user=employer_user)
        for i in range(10):
            Message.objects.create(conversation=conv, sender_id=employee_user.id, content=f'msg {i}')

        response = auth_client.get(f'/api/v1/chat/conversations/{conv.id}/messages/?limit=3')
        data = response.json()
        assert len(data['data']['results']) == 3
        assert data['data']['has_more'] is True

    def test_list_messages_unauthorized(self, auth_client):
        conv = Conversation.objects.create(subject='Private')
        response = auth_client.get(f'/api/v1/chat/conversations/{conv.id}/messages/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_mark_as_read(self, auth_client, employee_user, employer_user):
        conv = Conversation.objects.create(subject='Test')
        ConversationParticipant.objects.create(conversation=conv, user_id=employee_user.id)
        ConversationParticipant.objects.create(conversation=conv, user=employer_user)
        msg = Message.objects.create(conversation=conv, sender=employer_user, content='Unread')

        payload = {'conversation_id': str(conv.id)}
        response = auth_client.post('/api/v1/chat/messages/mark-read/', payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        msg.refresh_from_db()
        assert msg.is_read is True
        assert msg.read_at is not None

    def test_mark_as_read_invalid_conversation(self, auth_client):
        payload = {'conversation_id': str(uuid.uuid4())}
        response = auth_client.post('/api/v1/chat/messages/mark-read/', payload, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unread_count(self, auth_client, employee_user, employer_user):
        conv = Conversation.objects.create(subject='Test')
        ConversationParticipant.objects.create(conversation=conv, user_id=employee_user.id)
        ConversationParticipant.objects.create(conversation=conv, user=employer_user)
        Message.objects.create(conversation=conv, sender=employer_user, content='Unread msg 1')
        Message.objects.create(conversation=conv, sender=employer_user, content='Unread msg 2')

        response = auth_client.get('/api/v1/chat/messages/unread-count/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['data']['unread_count'] == 2

    def test_unread_count_no_unread(self, auth_client, employee_user, employer_user):
        conv = Conversation.objects.create(subject='Test')
        Message.objects.create(conversation=conv, sender=employer_user, content='Old msg')
        participant = ConversationParticipant.objects.create(
            conversation=conv, user_id=employee_user.id, last_read_at=timezone.now()
        )
        ConversationParticipant.objects.create(conversation=conv, user=employer_user)

        response = auth_client.get('/api/v1/chat/messages/unread-count/')
        data = response.json()
        assert data['data']['unread_count'] == 0

    def test_conversation_detail(self, auth_client, employee_user, employer_user):
        conv = Conversation.objects.create(subject='Detail Test')
        ConversationParticipant.objects.create(conversation=conv, user_id=employee_user.id)
        ConversationParticipant.objects.create(conversation=conv, user=employer_user)
        Message.objects.create(conversation=conv, sender_id=employee_user.id, content='Hello')

        response = auth_client.get(f'/api/v1/chat/conversations/{conv.id}/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['success'] is True
        assert data['data']['subject'] == 'Detail Test'

    def test_conversation_detail_not_participant(self, auth_client):
        conv = Conversation.objects.create(subject='Private')
        response = auth_client.get(f'/api/v1/chat/conversations/{conv.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_send_message_updates_last_message_at(self, auth_client, employee_user, employer_user):
        conv = Conversation.objects.create(subject='Test')
        ConversationParticipant.objects.create(conversation=conv, user_id=employee_user.id)
        ConversationParticipant.objects.create(conversation=conv, user=employer_user)

        payload = {'content': 'New message'}
        response = auth_client.post(f'/api/v1/chat/conversations/{conv.id}/messages/', payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        conv.refresh_from_db()
        assert conv.last_message_at is not None

    def test_unread_count_multiple_conversations(self, auth_client, employee_user, employer_user):
        for i in range(3):
            conv = Conversation.objects.create(subject=f'Conv {i}')
            ConversationParticipant.objects.create(conversation=conv, user_id=employee_user.id)
            ConversationParticipant.objects.create(conversation=conv, user=employer_user)
            Message.objects.create(conversation=conv, sender=employer_user, content=f'Unread {i}')

        response = auth_client.get('/api/v1/chat/messages/unread-count/')
        data = response.json()
        assert data['data']['unread_count'] == 3


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestChatWebSocket:
    async def test_websocket_connect(self):
        from rest_framework_simplejwt.tokens import AccessToken
        user = await database_sync_to_async(User.objects.create_user)(
            email='wsuser@example.com',
            password='Test@123456',
            name='WS User',
            phone='+919876543201',
            role='employee',
            is_verified=True,
        )
        token = AccessToken.for_user(user)
        communicator = WebsocketCommunicator(
            application,
            f'/ws/chat/?token={str(token)}',
        )
        connected, _ = await communicator.connect()
        assert connected
        response = await communicator.receive_json_from(timeout=5)
        assert response['type'] == 'connected'
        assert response['user_id'] == str(user.id)
        await communicator.disconnect()

    async def test_websocket_connect_invalid_token(self):
        communicator = WebsocketCommunicator(
            application,
            '/ws/chat/?token=invalidtoken123',
        )
        connected, _ = await communicator.connect()
        assert not connected

    async def test_websocket_connect_no_token(self):
        communicator = WebsocketCommunicator(
            application,
            '/ws/chat/',
        )
        connected, _ = await communicator.connect()
        assert not connected

    async def test_websocket_send_message(self):
        from rest_framework_simplejwt.tokens import AccessToken
        user1 = await database_sync_to_async(User.objects.create_user)(
            email='wsuser1@example.com',
            password='Test@123456',
            name='WS User 1',
            phone='+919876543202',
            role='employee',
            is_verified=True,
        )
        user2 = await database_sync_to_async(User.objects.create_user)(
            email='wsuser2@example.com',
            password='Test@123456',
            name='WS User 2',
            phone='+919876543203',
            role='employer',
            is_verified=True,
        )
        conv = await database_sync_to_async(Conversation.objects.create)(subject='WS Test')
        await database_sync_to_async(ConversationParticipant.objects.create)(
            conversation=conv, user=user1,
        )
        await database_sync_to_async(ConversationParticipant.objects.create)(
            conversation=conv, user=user2,
        )

        token = AccessToken.for_user(user1)
        communicator = WebsocketCommunicator(
            application,
            f'/ws/chat/?token={str(token)}',
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.receive_json_from(timeout=5)

        await communicator.send_json_to({
            'type': 'send_message',
            'conversation_id': str(conv.id),
            'content': 'Hello from WebSocket!',
        })

        response = await communicator.receive_json_from(timeout=5)
        assert response['type'] == 'message_sent'
        assert response['data']['content'] == 'Hello from WebSocket!'
        assert response['data']['status'] == 'sent'

        await communicator.disconnect()

    async def test_websocket_send_message_invalid_conversation(self):
        from rest_framework_simplejwt.tokens import AccessToken
        user = await database_sync_to_async(User.objects.create_user)(
            email='wsuser3@example.com',
            password='Test@123456',
            name='WS User 3',
            phone='+919876543204',
            role='employee',
            is_verified=True,
        )
        token = AccessToken.for_user(user)
        communicator = WebsocketCommunicator(
            application,
            f'/ws/chat/?token={str(token)}',
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.receive_json_from(timeout=5)

        await communicator.send_json_to({
            'type': 'send_message',
            'conversation_id': str(uuid.uuid4()),
            'content': 'Hello!',
        })

        response = await communicator.receive_json_from(timeout=5)
        assert response['type'] == 'error'
        assert 'Conversation not found' in response['message']
        await communicator.disconnect()

    async def test_websocket_send_message_empty_content(self):
        from rest_framework_simplejwt.tokens import AccessToken
        user = await database_sync_to_async(User.objects.create_user)(
            email='wsuser4@example.com',
            password='Test@123456',
            name='WS User 4',
            phone='+919876543205',
            role='employee',
            is_verified=True,
        )
        token = AccessToken.for_user(user)
        communicator = WebsocketCommunicator(
            application,
            f'/ws/chat/?token={str(token)}',
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.receive_json_from(timeout=5)

        await communicator.send_json_to({
            'type': 'send_message',
            'conversation_id': str(uuid.uuid4()),
            'content': '',
        })

        response = await communicator.receive_json_from(timeout=5)
        assert response['type'] == 'error'
        await communicator.disconnect()

    async def test_websocket_invalid_json(self):
        from rest_framework_simplejwt.tokens import AccessToken
        user = await database_sync_to_async(User.objects.create_user)(
            email='wsuser5@example.com',
            password='Test@123456',
            name='WS User 5',
            phone='+919876543206',
            role='employee',
            is_verified=True,
        )
        token = AccessToken.for_user(user)
        communicator = WebsocketCommunicator(
            application,
            f'/ws/chat/?token={str(token)}',
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.receive_json_from(timeout=5)

        await communicator.send_to(text_data='not json')
        response = await communicator.receive_json_from(timeout=5)
        assert response['type'] == 'error'
        assert 'Invalid JSON' in response['message']
        await communicator.disconnect()

    async def test_websocket_unknown_message_type(self):
        from rest_framework_simplejwt.tokens import AccessToken
        user = await database_sync_to_async(User.objects.create_user)(
            email='wsuser6@example.com',
            password='Test@123456',
            name='WS User 6',
            phone='+919876543207',
            role='employee',
            is_verified=True,
        )
        token = AccessToken.for_user(user)
        communicator = WebsocketCommunicator(
            application,
            f'/ws/chat/?token={str(token)}',
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.receive_json_from(timeout=5)

        await communicator.send_json_to({
            'type': 'unknown_type',
            'data': 'test',
        })

        response = await communicator.receive_json_from(timeout=5)
        assert response['type'] == 'error'
        await communicator.disconnect()

    async def test_websocket_receive_unauthorized(self):
        communicator = WebsocketCommunicator(
            application,
            '/ws/chat/?token=bad_token',
        )
        connected, _ = await communicator.connect()
        assert not connected

    async def test_websocket_typing_indicator(self):
        from rest_framework_simplejwt.tokens import AccessToken
        user1 = await database_sync_to_async(User.objects.create_user)(
            email='wstype1@example.com',
            password='Test@123456',
            name='WS Type 1',
            phone='+919876543208',
            role='employee',
            is_verified=True,
        )
        user2 = await database_sync_to_async(User.objects.create_user)(
            email='wstype2@example.com',
            password='Test@123456',
            name='WS Type 2',
            phone='+919876543209',
            role='employer',
            is_verified=True,
        )
        conv = await database_sync_to_async(Conversation.objects.create)(subject='Type Test')
        await database_sync_to_async(ConversationParticipant.objects.create)(
            conversation=conv, user=user1,
        )
        await database_sync_to_async(ConversationParticipant.objects.create)(
            conversation=conv, user=user2,
        )

        token = AccessToken.for_user(user1)
        communicator = WebsocketCommunicator(
            application,
            f'/ws/chat/?token={str(token)}',
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.receive_json_from(timeout=5)

        await communicator.send_json_to({
            'type': 'typing_start',
            'conversation_id': str(conv.id),
        })

        await communicator.disconnect()

    async def test_websocket_mark_read(self):
        from rest_framework_simplejwt.tokens import AccessToken
        user1 = await database_sync_to_async(User.objects.create_user)(
            email='wsread1@example.com',
            password='Test@123456',
            name='WS Read 1',
            phone='+919876543210',
            role='employee',
            is_verified=True,
        )
        user2 = await database_sync_to_async(User.objects.create_user)(
            email='wsread2@example.com',
            password='Test@123456',
            name='WS Read 2',
            phone='+919876543211',
            role='employer',
            is_verified=True,
        )
        conv = await database_sync_to_async(Conversation.objects.create)(subject='Read Test')
        await database_sync_to_async(ConversationParticipant.objects.create)(
            conversation=conv, user=user1,
        )
        await database_sync_to_async(ConversationParticipant.objects.create)(
            conversation=conv, user=user2,
        )
        await database_sync_to_async(Message.objects.create)(
            conversation=conv, sender=user2, content='Unread',
        )

        token = AccessToken.for_user(user1)
        communicator = WebsocketCommunicator(
            application,
            f'/ws/chat/?token={str(token)}',
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.receive_json_from(timeout=5)

        await communicator.send_json_to({
            'type': 'mark_read',
            'conversation_id': str(conv.id),
        })

        await communicator.disconnect()
