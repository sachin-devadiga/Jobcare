from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'logo', 'banner_image', 'images',
            'description', 'website', 'industry', 'company_size',
            'founded_year', 'headquarters', 'locations',
            'verification_status', 'verification_document',
            'is_featured', 'social_links', 'contact_email', 'contact_phone',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'verification_status', 'created_at', 'updated_at']

    def validate_website(self, value):
        if value and not value.startswith(('http://', 'https://')):
            value = 'https://' + value
        return value

    def validate_founded_year(self, value):
        if value is not None:
            from datetime import datetime
            current_year = datetime.now().year
            if value < 1800 or value > current_year:
                raise serializers.ValidationError(
                    _(f'Founded year must be between 1800 and {current_year}')
                )
        return value


class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'logo', 'industry',
            'headquarters', 'verification_status', 'is_featured',
        ]
        read_only_fields = fields


class CompanyVerifySerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['verified', 'rejected'])
    notes = serializers.CharField(required=False, allow_blank=True)
