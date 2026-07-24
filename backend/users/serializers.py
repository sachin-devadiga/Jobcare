from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import EmployeeProfile


class EmployeeProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = [
            'id', 'user', 'user_email', 'user_role',
            'full_name', 'avatar', 'date_of_birth', 'gender',
            'address', 'city', 'state', 'pincode', 'latitude', 'longitude',
            'skills', 'experience_years', 'education', 'experiences', 'languages', 'certificates',
            'resume_url', 'voice_resume_url', 'expected_salary',
            'preferred_job_categories', 'preferred_locations',
            'availability', 'aadhaar_number', 'aadhaar_verified',
            'profile_completion_score', 'is_profile_complete',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'profile_completion_score', 'is_profile_complete', 'created_at', 'updated_at', 'aadhaar_verified']

    def validate_phone(self, value):
        if value and len(value) < 10:
            raise serializers.ValidationError(_('Phone number must be at least 10 digits'))
        return value

    def validate_expected_salary(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(_('Expected salary cannot be negative'))
        return value

    def validate_experience_years(self, value):
        if value < 0 or value > 50:
            raise serializers.ValidationError(_('Experience years must be between 0 and 50'))
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class EmployeeProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = [
            'id', 'full_name', 'avatar', 'city', 'state',
            'skills', 'experience_years',
            'availability', 'profile_completion_score', 'is_profile_complete',
            'created_at',
        ]
        read_only_fields = fields


class AadhaarVerificationSerializer(serializers.Serializer):
    aadhaar_number = serializers.CharField(min_length=12, max_length=12)

    def validate_aadhaar_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(_('Aadhaar number must be 12 digits'))
        return value
