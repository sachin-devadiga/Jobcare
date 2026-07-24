from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class ResumeScoreSerializer(serializers.Serializer):
    resume_text = serializers.CharField(help_text='Full text content of the resume')
    job_title = serializers.CharField(required=False, allow_blank=True)
    job_description = serializers.CharField(help_text='Job description text')
    skills_required = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    experience_min = serializers.IntegerField(required=False, default=0)
    experience_max = serializers.IntegerField(required=False, default=0)
    education_required = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    location = serializers.CharField(required=False, allow_blank=True)

    def validate_resume_text(self, value):
        if len(value.strip()) < 50:
            raise serializers.ValidationError(_('Resume text is too short. Minimum 50 characters.'))
        return value

    def validate_job_description(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError(_('Job description is too short. Minimum 20 characters.'))
        return value


class SkillGapSerializer(serializers.Serializer):
    user_skills = serializers.ListField(child=serializers.CharField(), help_text='Current skills of the user')
    target_skills = serializers.ListField(child=serializers.CharField(), help_text='Skills required for target job')
    target_job_title = serializers.CharField(required=False, allow_blank=True)


class SalaryPredictionSerializer(serializers.Serializer):
    job_title = serializers.CharField(help_text='Job title for salary prediction')
    experience = serializers.IntegerField(min_value=0, max_value=50, default=0)
    city = serializers.CharField(required=False, allow_blank=True, default='')
    skills = serializers.ListField(child=serializers.CharField(), required=False, default=list)


class CareerRecommendationSerializer(serializers.Serializer):
    skills = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    experience_years = serializers.FloatField(required=False, default=0)
    preferred_categories = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    current_role = serializers.CharField(required=False, allow_blank=True)


class JobRecommendationSerializer(serializers.Serializer):
    skills = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    preferred_categories = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    preferred_locations = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    city = serializers.CharField(required=False, allow_blank=True)


class FraudCheckSerializer(serializers.Serializer):
    check_type = serializers.ChoiceField(
        choices=['job', 'duplicate', 'application', 'employer'],
        help_text='Type of fraud check to perform',
    )
    title = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=False, allow_blank=True)
    salary_min = serializers.FloatField(required=False, allow_null=True)
    salary_max = serializers.FloatField(required=False, allow_null=True)
    contact_email = serializers.EmailField(required=False, allow_blank=True)
    cover_letter = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    employer_id = serializers.CharField(required=False, allow_blank=True)


class UpskillingSerializer(serializers.Serializer):
    current_skills = serializers.ListField(child=serializers.CharField(), help_text='Current skills')
    career_goal = serializers.CharField(help_text='Desired career path or job title')
