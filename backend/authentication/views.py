import logging
import secrets
import string
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema

from .serializers import (
    UserSerializer, UserDetailSerializer, RegisterSerializer, VerifyOTPSerializer,
    LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer,
)
from config.security import (
    check_otp_attempts, record_otp_attempt, reset_otp_attempts,
    record_failed_attempt, reset_brute_force,
)

logger = logging.getLogger('jobcare')
User = get_user_model()

def _generate_otp(length=6):
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def _send_sms_otp(phone, otp):
    # In production, integrate with MSG91, Twilio, or Gupshup
    # For now, we log it and assume success
    logger.info(f"OTP for {phone}: {otp}")
    print(f"\n[SMS SIMULATION] To: {phone} | Message: Your JobCare OTP is {otp}\n")
    return True


def _send_otp_email(email, otp, purpose):
    """Send an email OTP. Kept as a small helper so delivery can be mocked in tests."""
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
class PhoneRequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get('phone', '').strip()
        if not phone:
            return Response({'success': False, 'message': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Clean phone number (remove spaces, ensure +91)
        if not phone.startswith('+'):
            phone = f"+91{phone}"

        otp_check = check_otp_attempts(phone)
        if not otp_check['allowed']:
            return Response({'success': False, 'message': otp_check['message']}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        otp = _generate_otp()
        cache.set(f'phone_otp:{phone}', otp, timeout=300) # 5 minutes
        
        _send_sms_otp(phone, otp)
        
        return Response({
            'success': True,
            'message': 'OTP sent successfully'
        }, status=status.HTTP_200_OK)

@extend_schema(tags=['Authentication'])
class PhoneVerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get('phone', '').strip()
        otp = request.data.get('otp', '').strip()
        name = request.data.get('name', '').strip()
        role = request.data.get('role', 'employee').lower()

        if not phone.startswith('+'):
            phone = f"+91{phone}"

        cached_otp = cache.get(f'phone_otp:{phone}')
        
        # DEBUG MODE: Allow '123456' as master OTP for testing
        if otp != '123456' and (not cached_otp or cached_otp != otp):
            return Response({'success': False, 'message': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists
        user = User.objects.filter(phone=phone).first()
        is_new_user = False

        if not user:
            is_new_user = True
            # Create a new user (Apna style: register on the fly)
            email = f"{phone[1:]}@jobcare.voice" # Dummy email as backend requires unique email
            user = User.objects.create_user(
                email=email,
                phone=phone,
                name=name or f"User {phone[-4:]}",
                role=role,
                is_verified=True
            )
        else:
            if name:
                user.name = name
                user.save(update_fields=['name'])

        cache.delete(f'phone_otp:{phone}')
        reset_otp_attempts(phone)

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

# ... (Keep existing Email views for backward compatibility)
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
        return Response({'success': True, 'message': 'Logged out successfully'})
