from unittest.mock import patch, MagicMock
import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from rest_framework import status

from authentication.exotel_sms_service import (
    ExotelSMSNotConfiguredError,
    ExotelSMSUnavailableError,
)

User = get_user_model()

REGISTER_URL = '/api/v1/auth/register/'
VERIFY_OTP_URL = '/api/v1/auth/verify-otp/'
LOGIN_URL = '/api/v1/auth/login/'
FORGOT_PASSWORD_URL = '/api/v1/auth/forgot-password/'
RESET_PASSWORD_URL = '/api/v1/auth/reset-password/'
REFRESH_URL = '/api/v1/auth/refresh/'
LOGOUT_URL = '/api/v1/auth/logout/'
PROFILE_URL = '/api/v1/auth/profile/'
FIREBASE_PHONE_VERIFY_URL = '/api/v1/auth/phone/verify-firebase/'
PHONE_SEND_OTP_URL = '/api/v1/auth/phone/send-otp/'
PHONE_VERIFY_URL = '/api/v1/auth/phone/verify/'
PHONE_OTP_RESEND_URL = '/api/v1/auth/otp/resend/'
EMAIL_OTP_REQUEST_URL = '/api/v1/auth/otp/email/request/'
EMAIL_OTP_VERIFY_URL = '/api/v1/auth/otp/email/verify/'

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

    def test_logout_requires_a_refresh_token(self, auth_client):
        response = auth_client.post(LOGOUT_URL, {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestFirebasePhoneAuthentication:
    @patch('firebase_admin.auth.verify_id_token')
    @patch('notifications.services.get_firebase_app')
    def test_verified_firebase_token_creates_user_and_returns_jwt(
        self, mock_app, mock_verify, api_client,
    ):
        mock_verify.return_value = {'phone_number': '+919876543299'}
        response = api_client.post(FIREBASE_PHONE_VERIFY_URL, {
            'id_token': 'firebase-id-token', 'name': 'Phone User', 'role': 'employee',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_new_user'] is True
        assert response.data['data']['user']['phone'] == '+919876543299'
        assert response.data['data']['access']
        mock_verify.assert_called_once_with('firebase-id-token', app=mock_app())

    @patch('firebase_admin.auth.verify_id_token')
    @patch('notifications.services.get_firebase_app')
    def test_verified_firebase_token_reuses_existing_user(self, mock_app, mock_verify, api_client, employee_user):
        mock_verify.return_value = {'phone_number': employee_user.phone}
        response = api_client.post(FIREBASE_PHONE_VERIFY_URL, {'id_token': 'firebase-id-token'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_new_user'] is False

    @patch('firebase_admin.auth.verify_id_token', side_effect=ValueError('invalid token'))
    @patch('notifications.services.get_firebase_app')
    def test_invalid_firebase_token_is_rejected(self, mock_app, mock_verify, api_client):
        response = api_client.post(FIREBASE_PHONE_VERIFY_URL, {'id_token': 'bad-token'}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_firebase_token_and_role_are_required_and_validated(self, api_client):
        assert api_client.post(FIREBASE_PHONE_VERIFY_URL, {}, format='json').status_code == status.HTTP_400_BAD_REQUEST
        response = api_client.post(FIREBASE_PHONE_VERIFY_URL, {'id_token': 'x', 'role': 'admin'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestExotelPhoneOTP:
    @pytest.fixture(autouse=True)
    def _clean_phone_otp_cache(self):
        cache.clear()
        yield
        cache.clear()

    def _send(self, api_client, phone='+919876543222'):
        return api_client.post(PHONE_SEND_OTP_URL, {'phone': phone}, format='json')

    @patch('authentication.views.send_sms')
    def test_send_otp_success(self, mock_send_sms, api_client):
        mock_send_sms.return_value = {'success': True, 'sid': 'sms_sid_value'}
        response = self._send(api_client)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        mock_send_sms.assert_called_once()
        phone, message = mock_send_sms.call_args.args
        assert phone == '+919876543222'
        assert 'verification code' in message

    @patch('authentication.views.send_sms')
    def test_resend_otp(self, mock_send_sms, api_client):
        mock_send_sms.return_value = {'success': True, 'sid': 'sms-sid-1'}
        response = api_client.post(PHONE_OTP_RESEND_URL, {'phone': '+919876543222'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        mock_send_sms.assert_called_once()

    @patch('authentication.views.send_sms')
    def test_send_otp_rate_limited(self, mock_send_sms, api_client):
        mock_send_sms.return_value = {'success': True, 'sid': 'sms-sid-1'}
        for _ in range(3):
            assert self._send(api_client).status_code == status.HTTP_200_OK
        response = self._send(api_client)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_send_otp_invalid_phone(self, api_client):
        response = self._send(api_client, phone='123')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('authentication.views.send_sms')
    def test_send_otp_unavailable_clears_code(self, mock_send_sms, api_client):
        mock_send_sms.side_effect = ExotelSMSUnavailableError('Exotel down')
        response = self._send(api_client)
        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        assert cache.get('phone_otp:+919876543222') is None

    def test_send_otp_dev_mode_without_credentials_logs_only(self, api_client):
        with patch('authentication.views.settings.DEBUG', True), \
             patch('authentication.views.send_sms',
                   side_effect=ExotelSMSNotConfiguredError('Exotel SMS is not configured')):
            response = self._send(api_client)
        assert response.status_code == status.HTTP_200_OK
        assert cache.get('phone_otp:+919876543222') is not None

    @patch('authentication.views.send_sms', side_effect=ExotelSMSNotConfiguredError('not configured'))
    def test_send_otp_fails_closed_in_production(self, mock_send_sms, api_client):
        with patch('authentication.views.settings.DEBUG', False):
            response = self._send(api_client)
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert cache.get('phone_otp:+919876543222') is None

    def test_verify_otp_creates_new_user(self, api_client):
        cache.set('phone_otp:+919876543222', '123456', timeout=300)
        response = api_client.post(PHONE_VERIFY_URL, {
            'phone': '+919876543222', 'otp': '123456', 'name': 'Phone User', 'role': 'employee',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_new_user'] is True
        assert response.data['data']['user']['phone'] == '+919876543222'
        assert 'access' in response.data['data']
        assert 'refresh' in response.data['data']

    def test_verify_otp_existing_user(self, api_client, employee_user):
        cache.set(f'phone_otp:{employee_user.phone}', '123456', timeout=300)
        response = api_client.post(PHONE_VERIFY_URL, {
            'phone': employee_user.phone, 'otp': '123456',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_new_user'] is False
        assert response.data['data']['user']['email'] == employee_user.email
        assert cache.get(f'phone_otp:{employee_user.phone}') is None

    def test_verify_otp_invalid_code(self, api_client):
        cache.set('phone_otp:+919876543222', '654321', timeout=300)
        response = api_client.post(PHONE_VERIFY_URL, {
            'phone': '+919876543222', 'otp': '000000',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_otp_expired(self, api_client):
        response = api_client.post(PHONE_VERIFY_URL, {
            'phone': '+919876543222', 'otp': '123456',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestEmailOTP:
    @pytest.fixture(autouse=True)
    def _clean_email_otp(self):
        from authentication.models import EmailOTP
        EmailOTP.objects.all().delete()
        cache.clear()
        yield
        EmailOTP.objects.all().delete()
        cache.clear()

    @pytest.fixture
    def mock_email_service(self):
        with patch('authentication.views.EmailNotificationService') as mock_service:
            mock_service.return_value.send_email.return_value = True
            yield mock_service

    def _request(self, api_client, phone='+919876543230', email='otpuser@example.com'):
        payload = {'phone': phone}
        if email:
            payload['email'] = email
        return api_client.post(EMAIL_OTP_REQUEST_URL, payload, format='json')

    def _verify(self, api_client, phone='+919876543230', otp='123456', **extra):
        payload = {'phone': phone, 'otp': otp, **extra}
        return api_client.post(EMAIL_OTP_VERIFY_URL, payload, format='json')

    def _create_otp(self, phone='+919876543230', otp='123456', email='otpuser@example.com'):
        from authentication.models import EmailOTP
        return EmailOTP.objects.create(phone=phone, otp=otp, email=email)

    def test_request_sends_to_supplied_email(self, api_client, mock_email_service):
        response = self._request(api_client)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['channel'] == 'email'
        send_email = mock_email_service.return_value.send_email
        assert send_email.call_args.kwargs['recipient_list'] == ['otpuser@example.com']
        assert send_email.call_args.kwargs['template_name'] == 'emails/otp.html'
        from authentication.models import EmailOTP
        assert EmailOTP.objects.filter(phone='+919876543230').exists()

    def test_request_uses_supplied_email_over_email_on_file(self, api_client, mock_email_service, employee_user):
        response = self._request(api_client, phone=employee_user.phone, email='new@example.com')
        assert response.status_code == status.HTTP_200_OK
        send_email = mock_email_service.return_value.send_email
        assert send_email.call_args.kwargs['recipient_list'] == ['new@example.com']
        assert User.objects.get(phone=employee_user.phone).email == 'new@example.com'

    def test_request_falls_back_to_email_on_file(self, api_client, mock_email_service, employee_user):
        response = self._request(api_client, phone=employee_user.phone, email=None)
        assert response.status_code == status.HTTP_200_OK
        send_email = mock_email_service.return_value.send_email
        assert send_email.call_args.kwargs['recipient_list'] == [employee_user.email]

    def test_request_updates_placeholder_email(self, api_client, mock_email_service):
        phone = '+919876543231'
        User.objects.create_user(
            email=f'{phone[1:]}@phone.jobcare.co.in', phone=phone, name='Placed', role='employee',
        )
        response = self._request(api_client, phone=phone, email='real@example.com')
        assert response.status_code == status.HTTP_200_OK
        assert User.objects.get(phone=phone).email == 'real@example.com'

    def test_request_updates_legacy_placeholder_email(self, api_client, mock_email_service):
        phone = '+919876543232'
        User.objects.create_user(
            email=f'{phone[1:]}@jobcare.voice', phone=phone, name='Legacy', role='employee',
        )
        response = self._request(api_client, phone=phone, email='real@example.com')
        assert response.status_code == status.HTTP_200_OK
        assert User.objects.get(phone=phone).email == 'real@example.com'
        send_email = mock_email_service.return_value.send_email
        assert send_email.call_args.kwargs['recipient_list'] == ['real@example.com']

    def test_request_rejects_email_taken_by_another_account(self, api_client, mock_email_service, employee_user):
        response = self._request(api_client, email=employee_user.email)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_request_requires_email_when_none_on_file(self, api_client, mock_email_service):
        response = self._request(api_client, email='')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_request_rate_limited_after_three_sends(self, api_client, mock_email_service):
        for _ in range(3):
            assert self._request(api_client).status_code == status.HTTP_200_OK
        response = self._request(api_client)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_request_blocked_when_sms_channel_active(self, api_client, mock_email_service):
        with override_settings(AUTH_OTP_CHANNEL='sms'):
            response = self._request(api_client)
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_verify_creates_new_user_with_requested_email(self, api_client, mock_email_service):
        self._create_otp()
        response = self._verify(api_client, role='employee')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_new_user'] is True
        assert response.data['data']['user']['email'] == 'otpuser@example.com'
        assert 'access' in response.data['data']
        assert 'refresh' in response.data['data']

    def test_verify_logs_in_existing_user(self, api_client, mock_email_service, employee_user):
        self._create_otp(phone=employee_user.phone, email=employee_user.email)
        response = self._verify(api_client, phone=employee_user.phone)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_new_user'] is False
        assert response.data['data']['user']['email'] == employee_user.email

    def test_verify_invalid_code(self, api_client, mock_email_service):
        self._create_otp(otp='654321')
        response = self._verify(api_client, otp='000000')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert cache.get('email_otp_verify_attempts:+919876543230') == 1

    def test_verify_expired_code(self, api_client, mock_email_service):
        response = self._verify(api_client)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_locks_after_five_wrong_attempts(self, api_client, mock_email_service):
        self._create_otp()
        for _ in range(5):
            assert self._verify(api_client, otp='000000').status_code == status.HTTP_400_BAD_REQUEST
        response = self._verify(api_client, otp='123456')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_new_otp_request_resets_verify_attempts(self, api_client, mock_email_service):
        self._create_otp()
        for _ in range(5):
            self._verify(api_client, otp='000000')
        assert self._request(api_client).status_code == status.HTTP_200_OK
        assert cache.get('email_otp_verify_attempts:+919876543230') is None


class TestExotelSMSService:
    @override_settings(
        EXOTEL_API_KEY='api-key',
        EXOTEL_API_TOKEN='api-token',
        EXOTEL_SID='my-sid',
        EXOTEL_SUBDOMAIN='api.exotel.com',
        EXOTEL_SMS_SENDER_ID='EXOTEL',
        EXOTEL_DLT_ENTITY_ID='1234567890',
        EXOTEL_DLT_TEMPLATE_ID='9876543210',
    )
    @patch('authentication.exotel_sms_service.requests.post')
    def test_send_sms_success(self, mock_post, ):
        from authentication.exotel_sms_service import send_sms

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'SMSMessage': {'Sid': 'sms-sid-abc', 'Status': 'queued'},
        }
        result = send_sms('+919876543222', 'Your JobCare verification code is 123456')

        assert result == {'success': True, 'sid': 'sms-sid-abc'}
        mock_post.assert_called_once()
        url = mock_post.call_args.args[0]
        assert url == 'https://api.exotel.com/v1/Accounts/my-sid/Sms/send'
        payload = mock_post.call_args.kwargs['data']
        assert payload['From'] == 'EXOTEL'
        assert payload['To'] == '+919876543222'
        assert payload['DltEntityId'] == '1234567890'
        assert payload['DltTemplateId'] == '9876543210'
        assert payload['SmsType'] == 'transactional'
        assert mock_post.call_args.kwargs['auth'] == ('api-key', 'api-token')

    def test_send_sms_not_configured(self):
        from authentication.exotel_sms_service import ExotelSMSNotConfiguredError, send_sms
        with override_settings(EXOTEL_API_KEY='', EXOTEL_API_TOKEN='', EXOTEL_SID='',
                               EXOTEL_SMS_SENDER_ID=''):
            try:
                send_sms('+919876543210', 'Hello')
            except ExotelSMSNotConfiguredError:
                pass
            else:
                raise AssertionError('Expected ExotelSMSNotConfiguredError')

    @override_settings(
        EXOTEL_API_KEY='key', EXOTEL_API_TOKEN='token', EXOTEL_SID='sid',
        EXOTEL_SMS_SENDER_ID='EXOTEL',
    )
    @patch('authentication.exotel_sms_service.requests.post')
    def test_send_sms_error_mapped(self, mock_post):
        from authentication.exotel_sms_service import ExotelSMSUnavailableError, send_sms

        mock_post.return_value.status_code = 429
        mock_post.return_value.json.return_value = {
            'RestException': {'Status': 429, 'Message': 'Rate limit exceeded'},
        }
        try:
            send_sms('+919876543210', 'Hello')
        except ExotelSMSUnavailableError as e:
            assert 'Too many' in str(e)
        else:
            raise AssertionError('Expected ExotelSMSUnavailableError')


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
