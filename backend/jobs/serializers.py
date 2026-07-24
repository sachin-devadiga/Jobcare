from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Job, Category, Skill, City
from companies.serializers import CompanyListSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'description', 'is_active', 'sort_order']
        read_only_fields = ['id', 'slug']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'slug', 'category', 'is_active']
        read_only_fields = ['id', 'slug']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'state', 'latitude', 'longitude', 'is_active']


class JobListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.ImageField(source='company.logo', read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'company', 'company_name', 'company_logo',
            'category', 'job_type', 'location', 'city', 'state',
            'salary_min', 'salary_max', 'salary_type',
            'experience_min', 'experience_max',
            'status', 'is_featured', 'is_urgent',
            'openings', 'urgency',
            'views_count', 'application_count',
            'created_at', 'expires_at',
        ]
        read_only_fields = ['id', 'slug', 'views_count', 'application_count', 'save_count', 'created_at', 'updated_at']


class JobDetailSerializer(serializers.ModelSerializer):
    company_details = CompanyListSerializer(source='company', read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'slug', 'company', 'company_details',
            'employer', 'description', 'responsibilities', 'requirements',
            'category', 'category_details',
            'skills_required', 'experience_min', 'experience_max',
            'salary_min', 'salary_max', 'salary_type',
            'location', 'city', 'state', 'latitude', 'longitude',
            'job_type', 'shift_timing',
            'education_required', 'benefits',
            'openings', 'urgency',
            'status', 'is_featured', 'is_urgent',
            'views_count', 'application_count', 'save_count',
            'created_at', 'updated_at', 'expires_at',
        ]
        read_only_fields = ['id', 'slug', 'views_count', 'application_count', 'save_count', 'created_at', 'updated_at']


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'id', 'company', 'title', 'description', 'responsibilities', 'requirements',
            'category', 'skills_required', 'experience_min', 'experience_max',
            'salary_min', 'salary_max', 'salary_type',
            'location', 'city', 'state', 'latitude', 'longitude',
            'job_type', 'shift_timing',
            'education_required', 'benefits',
            'openings', 'urgency',
            'status', 'is_featured', 'is_urgent',
            'expires_at',
        ]

    def validate_experience(self, data):
        if data.get('experience_max', 0) > 0 and data.get('experience_min', 0) > data.get('experience_max', 0):
            raise serializers.ValidationError(
                _('Minimum experience cannot be greater than maximum experience')
            )
        return data

    def validate_salary(self, data):
        if data.get('salary_max') and data.get('salary_min'):
            if data['salary_min'] > data['salary_max']:
                raise serializers.ValidationError(
                    _('Minimum salary cannot be greater than maximum salary')
                )
        return data

    def validate(self, attrs):
        attrs = self.validate_experience(attrs)
        attrs = self.validate_salary(attrs)
        return attrs

    def create(self, validated_data):
        validated_data['employer'] = self.context['request'].user
        return super().create(validated_data)
