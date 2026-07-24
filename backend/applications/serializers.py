from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Application
from jobs.serializers import JobListSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            'id', 'job', 'employee', 'status',
            'cover_letter', 'resume_url', 'voice_resume_url',
            'ai_match_score', 'employer_notes', 'rejection_reason',
            'interview_date', 'interview_time', 'interview_location', 'interview_type',
            'offer_letter_url', 'joined_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'employee', 'ai_match_score', 'created_at', 'updated_at']


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['job', 'cover_letter', 'resume_url', 'voice_resume_url']

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError(_('Authentication required'))

        from applications.repositories.application_repository import ApplicationRepository
        repo = ApplicationRepository()
        if repo.check_existing_application(attrs['job'].id, request.user.id):
            raise serializers.ValidationError(_('You have already applied for this job'))
        if attrs['job'].status not in ('active',):
            raise serializers.ValidationError(_('This job is no longer accepting applications'))
        return attrs

    def create(self, validated_data):
        validated_data['employee'] = self.context['request'].user
        validated_data['status'] = 'applied'
        return super().create(validated_data)


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            'status', 'employer_notes', 'rejection_reason',
            'interview_date', 'interview_time', 'interview_location', 'interview_type',
            'offer_letter_url', 'joined_date',
        ]


class ApplicationDetailSerializer(serializers.ModelSerializer):
    job_details = JobListSerializer(source='job', read_only=True)
    employee_email = serializers.EmailField(source='employee.email', read_only=True)
    employee_name = serializers.CharField(source='employee.employee_profile.full_name', read_only=True, default='')

    class Meta:
        model = Application
        fields = [
            'id', 'job', 'job_details', 'employee', 'employee_email', 'employee_name',
            'status', 'cover_letter', 'resume_url', 'voice_resume_url',
            'ai_match_score', 'employer_notes', 'rejection_reason',
            'interview_date', 'interview_time', 'interview_location', 'interview_type',
            'offer_letter_url', 'joined_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'employee', 'created_at', 'updated_at']


class ApplicationStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Application.Status.choices)
    notes = serializers.CharField(required=False, allow_blank=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
