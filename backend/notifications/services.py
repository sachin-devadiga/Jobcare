import json
import logging
import requests
from typing import Optional, List, Dict
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger('jobcare')


def get_firebase_app():
    """Initialise Firebase Admin exactly once using environment-backed config."""
    import firebase_admin
    from firebase_admin import credentials

    required = ('type', 'project_id', 'private_key', 'client_email')
    if not all(settings.FIREBASE_CONFIG.get(key) for key in required):
        raise RuntimeError('Firebase Admin credentials are not configured')
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.Certificate(settings.FIREBASE_CONFIG))
    return firebase_admin.get_app()


class FCMNotificationService:
    def __init__(self):
        self.server_key = None
        self._initialize()

    def _initialize(self):
        try:
            from firebase_admin import messaging

            get_firebase_app()
            self._messaging = messaging
            self._initialized = True
        except Exception as e:
            logger.warning(f'Firebase initialization failed: {e}. Using HTTP API fallback.')
            self._initialized = False
            self.server_key = settings.FIREBASE_CONFIG.get('server_key', '')

    def send_push_notification(
        self,
        fcm_token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
    ) -> bool:
        if self._initialized:
            return self._send_via_admin_sdk(fcm_token, title, body, data or {})
        else:
            return self._send_via_http_api(fcm_token, title, body, data or {})

    def send_multicast(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict] = None,
    ) -> bool:
        if self._initialized:
            return self._send_multicast_via_admin_sdk(tokens, title, body, data or {})
        else:
            success = True
            for token in tokens:
                if not self._send_via_http_api(token, title, body, data or {}):
                    success = False
            return success

    def _send_via_admin_sdk(self, fcm_token: str, title: str, body: str, data: Dict) -> bool:
        try:
            message = self._messaging.Message(
                notification=self._messaging.Notification(title=title, body=body),
                data={k: str(v) for k, v in data.items()},
                token=fcm_token,
            )
            response = self._messaging.send(message)
            logger.info(f'FCM sent to {fcm_token}: {response}')
            return True
        except Exception as e:
            logger.error(f'FCM send error: {str(e)}')
            return False

    def _send_multicast_via_admin_sdk(self, tokens: List[str], title: str, body: str, data: Dict) -> bool:
        try:
            message = self._messaging.MulticastMessage(
                notification=self._messaging.Notification(title=title, body=body),
                data={k: str(v) for k, v in data.items()},
                tokens=tokens,
            )
            response = self._messaging.send_multicast(message)
            logger.info(f'FCM multicast: {response.success_count} success, {response.failure_count} failures')
            return response.failure_count < len(tokens)
        except Exception as e:
            logger.error(f'FCM multicast error: {str(e)}')
            return False

    def _send_via_http_api(self, fcm_token: str, title: str, body: str, data: Dict) -> bool:
        try:
            url = 'https://fcm.googleapis.com/fcm/send'
            headers = {
                'Authorization': f'key={self.server_key}',
                'Content-Type': 'application/json',
            }
            payload = {
                'to': fcm_token,
                'notification': {
                    'title': title,
                    'body': body,
                    'sound': 'default',
                    'badge': '1',
                },
                'data': {k: str(v) for k, v in data.items()},
                'priority': 'high',
            }
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            logger.info(f'FCM HTTP API response: {response.status_code}')
            return response.status_code == 200
        except Exception as e:
            logger.error(f'FCM HTTP API error: {str(e)}')
            return False


class EmailNotificationService:
    BREVO_API_URL = 'https://api.brevo.com/v3/smtp/email'

    def _get_api_key(self):
        return getattr(settings, 'BREVO_API_KEY', '') or getattr(settings, 'EMAIL_HOST_PASSWORD', '')

    def _get_from(self):
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '')
        from_name = getattr(settings, 'EMAIL_FROM_NAME', 'JobCare Voice')
        return {'email': from_email, 'name': from_name}

    def send_email(
        self,
        subject: str,
        recipient_list: List[str],
        template_name: str = None,
        context: Dict = None,
        html_message: str = None,
        plain_message: str = None,
    ) -> bool:
        api_key = self._get_api_key()
        if not api_key:
            logger.error('No Brevo API key configured')
            return False

        if html_message:
            html_content = html_message
            plain_content = strip_tags(html_message)
        elif template_name and context:
            html_content = render_to_string(template_name, context)
            plain_content = strip_tags(html_content)
        else:
            html_content = plain_message or ''
            plain_content = plain_message or ''

        payload = {
            'sender': self._get_from(),
            'to': [{'email': addr} for addr in recipient_list],
            'subject': subject,
            'htmlContent': html_content,
            'textContent': plain_content,
        }

        try:
            resp = requests.post(
                self.BREVO_API_URL,
                json=payload,
                headers={
                    'api-key': api_key,
                    'Content-Type': 'application/json',
                },
                timeout=10,
            )
            if resp.status_code in (200, 201):
                logger.info(f'Email sent: {subject} to {recipient_list}')
                return True
            logger.error(f'Brevo API error {resp.status_code}: {resp.text[:300]}')
            return False
        except Exception as e:
            logger.error(f'Email send error: {str(e)}')
            return False

    def send_otp_email(self, email: str, otp: str) -> bool:
        subject = 'Your JobCare OTP Code'
        html_message = f'''
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>JobCare Verification</h2>
            <p>Your OTP code is:</p>
            <h1 style="color: #2563eb; font-size: 32px; letter-spacing: 5px;">{otp}</h1>
            <p>This code will expire in 5 minutes.</p>
            <p>If you did not request this, please ignore this email.</p>
        </body>
        </html>
        '''
        return self.send_email(subject, [email], html_message=html_message)

    def send_application_confirmation(self, email: str, job_title: str, company_name: str) -> bool:
        subject = f'Application Submitted - {job_title}'
        html_message = f'''
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Application Received!</h2>
            <p>Your application for <strong>{job_title}</strong> at <strong>{company_name}</strong> has been submitted.</p>
            <p>We will keep you updated on the status.</p>
        </body>
        </html>
        '''
        return self.send_email(subject, [email], html_message=html_message)

    def send_status_update(self, email: str, job_title: str, status: str) -> bool:
        subject = f'Application Status Update - {job_title}'
        html_message = f'''
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Application Status Updated</h2>
            <p>Your application for <strong>{job_title}</strong> has been updated to: <strong>{status}</strong></p>
        </body>
        </html>
        '''
        return self.send_email(subject, [email], html_message=html_message)


class NotificationService:
    def __init__(self):
        self.fcm = FCMNotificationService()
        self.email = EmailNotificationService()
        from .repositories.notification_repository import NotificationRepository, DeviceRepository
        self.notification_repo = NotificationRepository()
        self.device_repo = DeviceRepository()

    def send_and_notify(
        self,
        recipient_id,
        notification_type,
        title,
        body,
        data=None,
        send_push=True,
        send_email_notification=False,
    ) -> Optional['Notification']:
        from .models import Notification

        notification = Notification.objects.create(
            recipient_id=recipient_id,
            notification_type=notification_type,
            title=title,
            body=body,
            data=data or {},
            is_sent=True,
        )

        if send_push:
            self._send_push(recipient_id, title, body, data)

        return notification

    def _send_push(self, user_id, title, body, data):
        devices = self.device_repo.get_active_devices(user_id)
        tokens = [d.fcm_token for d in devices if d.fcm_token]
        if tokens:
            self.fcm.send_multicast(tokens, title, body, data)
