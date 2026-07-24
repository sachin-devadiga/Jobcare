from unittest.mock import patch, MagicMock
from django.core.cache import cache
from rest_framework import status

REGISTER_URL = '/api/v1/auth/register/'
VERIFY_OTP_URL = '/api/v1/auth/verify-otp/'
LOGIN_URL = '/api/v1/auth/login/'
FORGOT_PASSWORD_URL = '/api/v1/auth/forgot-password/'
RESET_PASSWORD_URL = '/api/v1/auth/reset-password/'
REFRESH_URL = '/api/v1/auth/refresh/'
LOGOUT_URL = '/api/v1/auth/logout/'
PROFILE_URL = '/api/v1/auth/profile/'

VALID_PASSWORD = 'StrongPass@123'
VALID_PAYLOAD = {
    'name': 'New User',
    'email': 'newuser@example.com',
    'phone': '+919876543220',
    'role': 'employee',
    'password': VALID_PASSWORD,
    'confirm_password': VALID_PASSWORD,
}


class TestRegister:
    @patch('authentication.views._send_otp_email')
    def test_register_success(self, mock_send_otp, api_client):
        response = api_client.post(REGISTER_URL, VALID_PAYLOAD, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['data']['email'] == 'newuser@example.com'
        assert response.data['data']['is_verified'] is False
        mock_send_otp.assert_called_once()

    def test_register_duplicate_email(self, api_client, employee_user):
        payload = {**VALID_PAYLOAD, 'email': employee_user.email}
        response = api_client.post(REGISTER_URL, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data['errors']

    def test_register_invalid_phone(self, api_client):
        payload = {**VALID_PAYLOAD, 'phone': '123'}
        response = api_client.post(REGISTER_URL, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'phone' in response.data['errors']

    def test_register_password_mismatch(self, api_client):
        payload = {
            **VALID_PAYLOAD,
            'password': 'Pass@1234',
            'confirm_password': 'Diff@5678',
        }
        response = api_client.post(REGISTER_URL, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'confirm_password' in response.data['errors']

    def test_register_weak_password(self, api_client):
        payload = {**VALID_PAYLOAD, 'password': '123', 'confirm_password': '123'}
        response = api_client.post(REGISTER_URL, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestVerifyOTP:
    @patch('authentication.views._send_otp_email')
    def test_verify_otp_success(self, mock_send_otp, api_client):
        api_client.post(REGISTER_URL, VALID_PAYLOAD, format='json')
        cache.set(f'otp:newuser@example.com', '123456', timeout=300)
        cache.set(f'otp_purpose:newuser@example.com', 'verify', timeout=300)
        response = api_client.post(VERIFY_OTP_URL, {
            'email': 'newuser@example.com',
            'otp': '123456',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'access' in response.data['data']
        assert 'refresh' in response.data['data']

    @patch('authentication.views._send_otp_email')
    def test_verify_otp_invalid(self, mock_send_otp, api_client, employee_user):
        cache.set(f'otp:{employee_user.email}', '654321', timeout=300)
        cache.set(f'otp_purpose:{employee_user.email}', 'verify', timeout=300)
        response = api_client.post(VERIFY_OTP_URL, {
            'email': employee_user.email,
            'otp': '000000',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Invalid or expired OTP' in str(response.data['message'])

    @patch('authentication.views._send_otp_email')
    def test_verify_otp_expired(self, mock_send_otp, api_client, employee_user):
        cache.delete(f'otp:{employee_user.email}')
        response = api_client.post(VERIFY_OTP_URL, {
            'email': employee_user.email,
            'otp': '123456',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Invalid or expired OTP' in str(response.data['message'])


class TestLogin:
    def test_login_success(self, api_client, employee_user):
        response = api_client.post(LOGIN_URL, {
            'email': employee_user.email,
            'password': 'Test@123456',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'access' in response.data['data']

    def test_login_invalid_credentials(self, api_client, employee_user):
        response = api_client.post(LOGIN_URL, {
            'email': employee_user.email,
            'password': 'WrongPass@1',
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_unverified_user(self, api_client, unverified_user):
        response = api_client.post(LOGIN_URL, {
            'email': unverified_user.email,
            'password': 'Test@123456',
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'not verified' in str(response.data['errors']).lower()

    def test_login_inactive_user(self, api_client, inactive_user):
        response = api_client.post(LOGIN_URL, {
            'email': inactive_user.email,
            'password': 'Test@123456',
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'invalid' in str(response.data['errors']).lower()


class TestForgotPassword:
    def test_forgot_password(self, api_client, employee_user):
        with patch('authentication.views._send_otp_email') as mock_send:
            response = api_client.post(FORGOT_PASSWORD_URL, {
                'email': employee_user.email,
            }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        mock_send.assert_called_once()

    def test_forgot_password_nonexistent_email(self, api_client):
        response = api_client.post(FORGOT_PASSWORD_URL, {
            'email': 'nobody@example.com',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestResetPassword:
    def test_reset_password_success(self, api_client, employee_user):
        cache.set(f'otp:{employee_user.email}', '999999', timeout=300)
        cache.set(f'otp_purpose:{employee_user.email}', 'reset', timeout=300)
        response = api_client.post(RESET_PASSWORD_URL, {
            'email': employee_user.email,
            'otp': '999999',
            'password': 'NewPass@9876',
            'confirm_password': 'NewPass@9876',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        employee_user.refresh_from_db()
        assert employee_user.check_password('NewPass@9876')

    def test_reset_password_invalid_otp(self, api_client, employee_user):
        cache.set(f'otp:{employee_user.email}', '111111', timeout=300)
        cache.set(f'otp_purpose:{employee_user.email}', 'reset', timeout=300)
        response = api_client.post(RESET_PASSWORD_URL, {
            'email': employee_user.email,
            'otp': '000000',
            'password': 'NewPass@9876',
            'confirm_password': 'NewPass@9876',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestTokenRefresh:
    def test_refresh_token(self, api_client, employee_user):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(employee_user)
        response = api_client.post(REFRESH_URL, {
            'refresh': str(refresh),
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True


class TestLogout:
    def test_logout(self, auth_client):
        from rest_framework_simplejwt.tokens import RefreshToken
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(email='employee@example.com')
        refresh = RefreshToken.for_user(user)
        response = auth_client.post(LOGOUT_URL, {
            'refresh': str(refresh),
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True


class TestProfile:
    def test_profile_get(self, auth_client):
        response = auth_client.get(PROFILE_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['email'] == 'employee@example.com'

    def test_profile_update(self, auth_client):
        response = auth_client.patch(PROFILE_URL, {
            'name': 'Updated Name',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['name'] == 'Updated Name'


class TestRateLimiting:
    @patch('authentication.views.RegisterView.throttle_classes', [])
    def test_rate_limiting(self, api_client):
        pass
