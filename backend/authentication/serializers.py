import re
import secrets
import string
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from config.validators import validate_password_complexity, validate_phone_number
from config.security import check_otp_attempts, check_brute_force

User = get_user_model()


def generate_numeric_otp(length=6):
    return ''.join(secrets.choice(string.digits) for _ in range(length))


class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, min_length=1, max_length=255)
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)
    confirm_password = serializers.CharField(write_only=True, min_length=8, max_length=128)

    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'role', 'password', 'confirm_password']

    def validate_email(self, value):
        cleaned = value.lower().strip()
        if User.objects.filter(email=cleaned).exists():
            raise serializers.ValidationError(_('A user with this email already exists'))
        return cleaned

    def validate_phone(self, value):
        cleaned = validate_phone_number(value)
        if User.objects.filter(phone=cleaned).exists():
            raise serializers.ValidationError(_('A user with this phone already exists'))
        return cleaned

    def validate_role(self, value):
        if value not in [User.Role.EMPLOYEE, User.Role.EMPLOYER]:
            raise serializers.ValidationError(_('Role must be employee or employer'))
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
            validate_password_complexity(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password': _('Passwords do not match')})
        return attrs

    def create(self, validated_data):
        validated_data['is_active'] = True
        validated_data['is_verified'] = False
        user = User.objects.create_user(**validated_data)
        return user


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)

    def validate_email(self, value):
        email_clean = value.lower().strip()
        try:
            User.objects.get(email=email_clean)
        except User.DoesNotExist:
            raise serializers.ValidationError(_('No user found with this email'))
        otp_check = check_otp_attempts(email_clean)
        if not otp_check['allowed']:
            raise serializers.ValidationError(_('Too many OTP attempts. Please try again later.'))
        return email_clean

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(_('OTP must be numeric'))
        if len(value) != 6:
            raise serializers.ValidationError(_('OTP must be exactly 6 digits'))
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').lower().strip()
        phone = attrs.get('phone', '').strip()
        password = attrs.get('password', '')

        if not email and not phone:
            raise serializers.ValidationError(_('Email or phone is required'))

        if email:
            bf_check = check_brute_force(email, 'login')
            if bf_check['locked']:
                raise serializers.ValidationError(
                    _(f'Account temporarily locked. Try again in {bf_check["remaining_seconds"]} seconds.')
                )
            user = authenticate(request=self.context.get('request'), email=email, password=password)
        else:
            try:
                user_obj = User.objects.get(phone=phone)
                bf_check = check_brute_force(user_obj.email, 'login')
                if bf_check['locked']:
                    raise serializers.ValidationError(
                        _(f'Account temporarily locked. Try again in {bf_check["remaining_seconds"]} seconds.')
                    )
                user = authenticate(request=self.context.get('request'), email=user_obj.email, password=password)
            except User.DoesNotExist:
                user = None

        if not user:
            raise serializers.ValidationError(_('Invalid credentials'))
        if not user.is_active:
            raise serializers.ValidationError(_('Account is deactivated'))
        if not user.is_verified:
            raise serializers.ValidationError(_('Email not verified. Please verify your email'))

        refresh = RefreshToken.for_user(user)
        attrs['user'] = user
        attrs['refresh'] = str(refresh)
        attrs['refresh_obj'] = refresh
        attrs['access'] = str(refresh.access_token)
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        email_clean = value.lower().strip()
        try:
            User.objects.get(email=email_clean)
        except User.DoesNotExist:
            raise serializers.ValidationError(_('No user found with this email'))
        otp_check = check_otp_attempts(email_clean)
        if not otp_check['allowed']:
            raise serializers.ValidationError(_('Too many OTP requests. Please try again later.'))
        return email_clean


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)
    password = serializers.CharField(min_length=8, max_length=128)
    confirm_password = serializers.CharField(min_length=8, max_length=128)

    def validate_email(self, value):
        email_clean = value.lower().strip()
        try:
            User.objects.get(email=email_clean)
        except User.DoesNotExist:
            raise serializers.ValidationError(_('No user found with this email'))
        return email_clean

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(_('OTP must be numeric'))
        if len(value) != 6:
            raise serializers.ValidationError(_('OTP must be exactly 6 digits'))
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
            validate_password_complexity(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': _('Passwords do not match')})
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone', 'role', 'is_verified', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_verified', 'is_active', 'created_at', 'updated_at']


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone', 'role', 'is_verified', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_verified', 'is_active', 'created_at', 'updated_at']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['email'] = user.email
        return token


class SendPhoneOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)

    def validate_phone(self, value):
        return validate_phone_number(value)


class EmailOTPRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate_phone(self, value):
        return validate_phone_number(value)

    def validate_email(self, value):
        return (value or '').lower().strip()


class EmailOTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    otp = serializers.CharField(min_length=6, max_length=6)
    name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    role = serializers.ChoiceField(
        choices=['employee', 'employer'],
        required=False,
        default='employee',
    )

    def validate_phone(self, value):
        return validate_phone_number(value)

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(_('OTP must be numeric'))
        return value


class VerifyPhoneOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    otp = serializers.CharField(min_length=6, max_length=6)
    name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    role = serializers.ChoiceField(
        choices=['employee', 'employer'],
        required=False,
        default='employee',
    )

    def validate_phone(self, value):
        return validate_phone_number(value)

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(_('OTP must be numeric'))
        return value
