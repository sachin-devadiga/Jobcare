import uuid
from rest_framework import status

NOTIFICATIONS_URL = '/api/v1/notifications/'
UNREAD_COUNT_URL = '/api/v1/notifications/unread-count/'
MARK_ALL_READ_URL = '/api/v1/notifications/mark-all-read/'
DEVICES_URL = '/api/v1/notifications/devices/'


class TestNotificationList:
    def test_list_notifications(self, auth_client, notification):
        response = auth_client.get(NOTIFICATIONS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']['results']) >= 1

    def test_list_notifications_unauthenticated(self, api_client):
        response = api_client.get(NOTIFICATIONS_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUnreadCount:
    def test_unread_count(self, auth_client, notification):
        response = auth_client.get(UNREAD_COUNT_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['unread_count'] >= 1

    def test_unread_count_zero(self, auth_client):
        response = auth_client.get(UNREAD_COUNT_URL)
        assert response.status_code == status.HTTP_200_OK
        assert 'unread_count' in response.data['data']


class TestMarkRead:
    def test_mark_read(self, auth_client, notification):
        url = f'/api/v1/notifications/{notification.id}/read/'
        response = auth_client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        notification.refresh_from_db()
        assert notification.is_read is True

    def test_mark_read_not_found(self, auth_client):
        url = f'/api/v1/notifications/{uuid.uuid4()}/read/'
        response = auth_client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_mark_read_unauthorized_user(self, employer_auth_client, notification):
        url = f'/api/v1/notifications/{notification.id}/read/'
        response = employer_auth_client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestMarkAllRead:
    def test_mark_all_read(self, auth_client, notification):
        response = auth_client.post(MARK_ALL_READ_URL, {}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        from notifications.models import Notification
        unread = Notification.objects.filter(recipient__isnull=False, is_read=False).count()
        assert unread == 0


class TestDeviceRegistration:
    def test_register_device(self, auth_client):
        response = auth_client.post(DEVICES_URL, {
            'fcm_token': 'test-fcm-token-12345',
            'platform': 'android',
            'device_id': 'device-001',
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True

    def test_register_device_duplicate_token(self, auth_client, employee_user):
        from notifications.models import Device
        Device.objects.create(
            user=employee_user,
            fcm_token='dup-token',
            platform='android',
        )
        response = auth_client.post(DEVICES_URL, {
            'fcm_token': 'dup-token',
            'platform': 'android',
            'device_id': 'device-002',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_list_devices(self, auth_client, notification, employee_user):
        from notifications.models import Device
        Device.objects.create(
            user=employee_user,
            fcm_token='list-test-token',
            platform='ios',
        )
        response = auth_client.get(DEVICES_URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) >= 1

    def test_register_device_unauthenticated(self, api_client):
        response = api_client.post(DEVICES_URL, {
            'fcm_token': 'no-auth-token',
            'platform': 'web',
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
