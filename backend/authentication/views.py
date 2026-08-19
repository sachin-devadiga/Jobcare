import logging
import secrets
import string
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema

from .serializers import (
    UserSerializer, UserDetailSerializer, RegisterSerializer, VerifyOTPSerializer,
    LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer,
    SendPhoneOTPSerializer, VerifyPhoneOTPSerializer,
    EmailOTPRequestSerializer, EmailOTPVerifySerializer,
)
from config.security import (
    check_otp_attempts, record_otp_attempt, reset_otp_attempts,
    record_failed_attempt, reset_brute_force,
)
from .exotel_sms_service import (
    send_sms,
    ExotelSMSError,
    ExotelSMSNotConfiguredError,
)
from notifications.services import EmailNotificationService

logger = logging.getLogger('jobcare')
User = get_user_model()

PHONE_EMAIL_SUFFIX = '@phone.blieve.in'
# Legacy placeholder suffixes stay recognized so older accounts self-heal on
# their next OTP request (see EmailOTPRequestView).
INTERNAL_EMAIL_SUFFIXES = ('@phone.blieve.in', '@phone.jobcare.co.in', '@jobcare.voice')
EMAIL_OTP_TTL = 300
EMAIL_OTP_MAX_SENDS = 3
EMAIL_OTP_VERIFY_MAX_ATTEMPTS = 5
EMAIL_OTP_VERIFY_ATTEMPT_WINDOW = 300

def _is_placeholder_email(email):
    return bool(email) and email.lower().endswith(INTERNAL_EMAIL_SUFFIXES)

def _generate_otp(length=6):
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def _send_phone_sms(phone, otp):
    """Deliver a phone OTP. In DEBUG without Plivo credentials, the OTP is
    logged instead of sent so local development and emulator testing work."""
    plivo_configured = bool(
        settings.PLIVO_AUTH_ID and settings.PLIVO_AUTH_TOKEN and settings.PLIVO_SENDER_NUMBER
    )
    if settings.DEBUG and not plivo_configured:
        logger.info(f'DEV OTP for {phone}: {otp} (Plivo not configured)')
        return True
    try:
        import plivo
        client = plivo.RestClient(settings.PLIVO_AUTH_ID, settings.PLIVO_AUTH_TOKEN)
        client.messages.create(
            src=settings.PLIVO_SENDER_NUMBER,
            dst=phone,
            text=f'Your JobCare verification code is {otp}. Valid for 5 minutes.',
        )
        logger.info(f'Plivo OTP sent to {phone}')
        return True
    except Exception as e:
        logger.error(f'Plivo SMS send failed for {phone}: {e}')
        return False

def _send_otp_email(email, otp, purpose):
    """Send an email OTP. Kept as a small helper so delivery can be mocked in tests."""
    if settings.DEBUG:
        logger.info(f'DEV OTP for {email}: {otp} ({purpose})')
    send_mail(
        subject='Your JobCare verification code',
        message=f'Your {purpose} verification code is {otp}. It expires in 5 minutes.',
        from_email=None,
        recipient_list=[email],
        fail_silently=True,
    )
    return True


def _tokens_for(user):
    refresh = RefreshToken.for_user(user)
    return {'user': UserSerializer(user).data, 'access': str(refresh.access_token), 'refresh': str(refresh)}


class RefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            return Response({'success': True, 'data': response.data})
        return response


@extend_schema(tags=['Authentication'])
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        otp = _generate_otp()
        cache.set(f'otp:{user.email}', otp, timeout=300)
        cache.set(f'otp_purpose:{user.email}', 'verify', timeout=300)
        _send_otp_email(user.email, otp, 'account')
        return Response({'success': True, 'data': UserSerializer(user).data}, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Authentication'])
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        email, otp = serializer.validated_data['email'], serializer.validated_data['otp']
        if cache.get(f'otp:{email}') != otp or cache.get(f'otp_purpose:{email}') != 'verify':
            record_otp_attempt(email)
            return Response({'success': False, 'message': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(email=email)
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        cache.delete(f'otp:{email}')
        cache.delete(f'otp_purpose:{email}')
        reset_otp_attempts(email)
        return Response({'success': True, 'data': _tokens_for(user)})


@extend_schema(tags=['Authentication'])
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            identifier = request.data.get('email') or request.data.get('phone') or ''
            if identifier:
                record_failed_attempt(identifier, 'login')
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_401_UNAUTHORIZED)
        user = serializer.validated_data['user']
        reset_brute_force(user.email, 'login')
        return Response({'success': True, 'data': _tokens_for(user)})


@extend_schema(tags=['Authentication'])
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data['email']
        otp = _generate_otp()
        cache.set(f'otp:{email}', otp, timeout=300)
        cache.set(f'otp_purpose:{email}', 'reset', timeout=300)
        _send_otp_email(email, otp, 'password reset')
        return Response({'success': True, 'message': 'Password reset OTP sent'})


@extend_schema(tags=['Authentication'])
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        email, otp = serializer.validated_data['email'], serializer.validated_data['otp']
        if cache.get(f'otp:{email}') != otp or cache.get(f'otp_purpose:{email}') != 'reset':
            record_otp_attempt(email)
            return Response({'success': False, 'message': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(email=email)
        user.set_password(serializer.validated_data['password'])
        user.save(update_fields=['password'])
        cache.delete(f'otp:{email}')
        cache.delete(f'otp_purpose:{email}')
        reset_otp_attempts(email)
        return Response({'success': True, 'message': 'Password reset successfully'})

@extend_schema(tags=['Authentication'])
class FirebasePhoneVerifyView(APIView):
    """Exchange a Firebase Phone Auth ID token for JobCare JWT tokens."""
    permission_classes = [AllowAny]

    def post(self, request):
        id_token = request.data.get('id_token', '').strip()
        name = request.data.get('name', '').strip()
        role = request.data.get('role', 'employee').lower()

        if not id_token:
            return Response({'success': False, 'message': 'Firebase ID token is required'}, status=status.HTTP_400_BAD_REQUEST)
        if role not in (User.Role.EMPLOYEE, User.Role.EMPLOYER):
            return Response({'success': False, 'message': 'Invalid user role'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from firebase_admin import auth as firebase_auth
            from notifications.services import get_firebase_app
            decoded_token = firebase_auth.verify_id_token(id_token, app=get_firebase_app())
        except Exception:
            logger.exception('Firebase phone token verification failed')
            return Response({'success': False, 'message': 'Phone verification failed'}, status=status.HTTP_401_UNAUTHORIZED)

        phone = decoded_token.get('phone_number')
        if not phone:
            return Response({'success': False, 'message': 'Verified Firebase token has no phone number'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(phone=phone).first()
        is_new_user = False

        if not user:
            is_new_user = True
            # Firebase Phone Auth does not guarantee an email. This internal,
            # unique placeholder is never shown as a contact email.
            email = f"{phone[1:]}{PHONE_EMAIL_SUFFIX}"
            user = User.objects.create_user(
                email=email,
                phone=phone,
                name=name,
                role=role,
                is_verified=True
            )
        else:
            if name:
                user.name = name
                user.save(update_fields=['name'])

        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'is_new_user': is_new_user,
            'data': {
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_200_OK)


@extend_schema(tags=['Authentication'])
class SendPhoneOTPView(APIView):
    """Generate a 6-digit OTP and deliver it via Exotel SMS.

    OTP state (code, 5-minute expiry, 3 sends per 5 minutes) is kept in
    cache and is vendor-agnostic; only the send call touches Exotel.
    Also serves as the resend endpoint — code generation is idempotent
    with respect to the SMS vendor.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendPhoneOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone']

        attempts_key = f'phone_otp_attempts:{phone}'
        attempts = cache.get(attempts_key, 0)
        if attempts >= 3:
            logger.warning(f'Phone OTP rate limit hit for {phone}')
            return Response(
                {'success': False, 'message': 'Too many OTP requests. Try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        otp = _generate_otp()
        cache.set(f'phone_otp:{phone}', otp, timeout=300)

        try:
            send_sms(phone, f'Your JobCare verification code is {otp}. Valid for 5 minutes.')
        except ExotelSMSNotConfiguredError:
            if settings.DEBUG:
                logger.info(f'DEV OTP for {phone}: {otp} (Exotel SMS not configured)')
            else:
                cache.delete(f'phone_otp:{phone}')
                return Response(
                    {'success': False, 'message': 'SMS service is not configured.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
        except ExotelSMSError as e:
            cache.delete(f'phone_otp:{phone}')
            logger.error(f'Exotel SMS send failed for {phone}: {e}')
            return Response(
                {'success': False, 'message': 'Failed to send OTP. Please try again.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        cache.set(attempts_key, attempts + 1, timeout=300)
        return Response({'success': True, 'message': 'OTP sent successfully'})


@extend_schema(tags=['Authentication'])
class VerifyPhoneOTPView(APIView):
    """Verify a phone OTP — creates user on first verification or logs in existing."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyPhoneOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone']
        otp = serializer.validated_data['otp']

        cached_otp = cache.get(f'phone_otp:{phone}')
        if cached_otp is None or secrets.compare_digest(str(cached_otp), str(otp)) is False:
            return Response(
                {'success': False, 'message': 'Invalid or expired OTP'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache.delete(f'phone_otp:{phone}')
        cache.delete(f'phone_otp_attempts:{phone}')

        user = User.objects.filter(phone=phone).first()
        is_new_user = False

        if not user:
            is_new_user = True
            clean = phone.lstrip('+')
            email = f"{clean}{PHONE_EMAIL_SUFFIX}"
            name = serializer.validated_data.get('name', '')
            role = serializer.validated_data.get('role', 'employee')
            user = User.objects.create_user(
                email=email,
                phone=phone,
                name=name,
                role=role,
                is_verified=True,
            )
        else:
            name = serializer.validated_data.get('name', '')
            if name:
                user.name = name
                user.save(update_fields=['name'])

        return Response({
            'success': True,
            'is_new_user': is_new_user,
            'data': _tokens_for(user),
        }, status=status.HTTP_200_OK)


@extend_schema(tags=['Authentication'])
class EmailOTPRequestView(APIView):
    """Generate a 6-digit OTP and deliver it via email.

    Temporary/parallel channel while Exotel SMS is blocked on DLT approval.
    Mirrors the SMS OTP flow: 5-minute expiry, 3 sends per 5 minutes.
    The recipient email resolves to the user's email on file when it is a
    real address, otherwise falls back to the email supplied in the request.
    Gated by settings.AUTH_OTP_CHANNEL — flip to 'sms' when DLT clears and
    this path is disabled (the SMS path takes over via the phone endpoints).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        if settings.AUTH_OTP_CHANNEL != 'email':
            return Response(
                {'success': False, 'message': 'SMS OTP channel is active. Use the phone OTP endpoints.'},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = EmailOTPRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone']
        provided_email = serializer.validated_data.get('email', '')

        from authentication.models import EmailOTP

        user = User.objects.filter(phone=phone).first()
        email = ''
        if provided_email:
            email = provided_email
            taken = User.objects.filter(email=email).exclude(pk=getattr(user, 'pk', None)).exists()
            if taken:
                return Response(
                    {'success': False, 'message': 'This email is already linked to another account.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if user:
                user.email = email
                user.save(update_fields=['email'])
        elif user and user.email and not _is_placeholder_email(user.email):
            email = user.email
        if not email:
            return Response(
                {'success': False, 'message': 'An email address is required for this account.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        recent_cutoff = timezone.now() - timezone.timedelta(minutes=5)
        attempts = EmailOTP.objects.filter(phone=phone, created_at__gte=recent_cutoff).count()
        if attempts >= EMAIL_OTP_MAX_SENDS:
            logger.warning(f'Email OTP rate limit hit for {phone}')
            return Response(
                {'success': False, 'message': 'Too many OTP requests. Try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        otp = _generate_otp()
        EmailOTP.objects.filter(phone=phone, is_used=False).update(is_used=True)
        EmailOTP.objects.create(phone=phone, otp=otp, email=email)
        cache.delete(f'email_otp_verify_attempts:{phone}')

        smtp_configured = bool(settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD)
        if settings.DEBUG:
            logger.info(
                f'DEV OTP for {phone} ({email}): {otp} '
                f'(SMTP {"configured" if smtp_configured else "not configured"})'
            )
        if settings.DEBUG and not smtp_configured:
            pass
        elif not smtp_configured:
            logger.error('Email OTP requested but SMTP is not configured')
            return Response(
                {'success': False, 'message': 'Email service not configured. Please contact support.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        else:
            sent = EmailNotificationService().send_email(
                subject='Your JobCare OTP',
                recipient_list=[email],
                template_name='emails/otp.html',
                context={'otp': otp},
            )
            if not sent:
                return Response(
                    {'success': False, 'message': 'Failed to send OTP. Please try again.'},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

        return Response({
            'success': True,
            'message': 'OTP sent successfully',
            'channel': settings.AUTH_OTP_CHANNEL,
        })


@extend_schema(tags=['Authentication'])
class EmailOTPVerifyView(APIView):
    """Verify an email OTP — creates user on first verification or logs in existing."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailOTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone']
        otp = serializer.validated_data['otp']

        from authentication.models import EmailOTP

        verify_attempts_key = f'email_otp_verify_attempts:{phone}'
        verify_attempts = cache.get(verify_attempts_key, 0)
        if verify_attempts >= EMAIL_OTP_VERIFY_MAX_ATTEMPTS:
            logger.warning(f'Email OTP verify lockout hit for {phone}')
            return Response(
                {'success': False, 'message': 'Too many OTP attempts. Try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        otp_record = EmailOTP.objects.filter(phone=phone, is_used=False).order_by('-created_at').first()
        if otp_record is None or not otp_record.verify(otp):
            cache.set(verify_attempts_key, verify_attempts + 1, timeout=EMAIL_OTP_VERIFY_ATTEMPT_WINDOW)
            return Response(
                {'success': False, 'message': 'Invalid or expired OTP'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache.delete(verify_attempts_key)
        requested_email = otp_record.email or ''

        user = User.objects.filter(phone=phone).first()
        is_new_user = False

        if not user:
            is_new_user = True
            clean = phone.lstrip('+')
            email = requested_email or f'{clean}{PHONE_EMAIL_SUFFIX}'
            name = serializer.validated_data.get('name', '')
            role = serializer.validated_data.get('role', 'employee')
            user = User.objects.create_user(
                email=email,
                phone=phone,
                name=name,
                role=role,
                is_verified=True,
            )
        else:
            if requested_email and requested_email != user.email:
                user.email = requested_email
                user.save(update_fields=['email'])
            name = serializer.validated_data.get('name', '')
            if name:
                user.name = name
                user.save(update_fields=['name'])

        return Response({
            'success': True,
            'is_new_user': is_new_user,
            'data': _tokens_for(user),
        }, status=status.HTTP_200_OK)


@extend_schema(tags=['Authentication'])
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response({'success': True, 'data': serializer.data})

    def patch(self, request):
        serializer = UserDetailSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Profile updated', 'data': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Authentication'])
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response(
                {'success': False, 'message': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            return Response(
                {'success': False, 'message': 'Invalid refresh token'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'success': True, 'message': 'Logged out successfully'})
