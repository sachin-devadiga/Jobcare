from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import EmployerProfile
from companies.serializers import CompanySerializer


class EmployerProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    company_details = CompanySerializer(source='company', read_only=True)

    class Meta:
        model = EmployerProfile
        fields = [
            'id', 'user', 'user_email', 'company', 'company_details',
            'full_name', 'designation', 'phone_secondary',
            'is_verified', 'is_company_admin',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'is_verified', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class EmployerProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = ['id', 'full_name', 'designation', 'company', 'is_verified', 'is_company_admin']
        read_only_fields = fields
