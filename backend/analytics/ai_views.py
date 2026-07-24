import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .ai_services import (
    ResumeScoringService,
    SkillGapAnalysis,
    SalaryPredictionService,
    CareerRecommendationService,
    JobRecommendationEngine,
    FraudDetectionService,
)
from .ai_serializers import (
    ResumeScoreSerializer,
    SkillGapSerializer,
    SalaryPredictionSerializer,
    CareerRecommendationSerializer,
    JobRecommendationSerializer,
    FraudCheckSerializer,
    UpskillingSerializer,
)

logger = logging.getLogger('jobcare')


@extend_schema(tags=['AI Features'])
class ResumeScoreView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ResumeScoreSerializer,
        responses={200: OpenApiResponse(description='Resume scoring result')},
        description='Score a resume against job requirements',
    )
    def post(self, request):
        serializer = ResumeScoreSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        job_requirements = {
            'skills': serializer.validated_data.get('skills_required', []),
            'experience_min': serializer.validated_data.get('experience_min', 0),
            'experience_max': serializer.validated_data.get('experience_max', 0),
            'education': serializer.validated_data.get('education_required', []),
            'location': serializer.validated_data.get('location', ''),
        }

        result = ResumeScoringService.score_resume(
            serializer.validated_data['resume_text'],
            job_requirements,
        )

        return Response({'success': True, 'data': result}, status=status.HTTP_200_OK)


@extend_schema(tags=['AI Features'])
class SkillGapView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SkillGapSerializer,
        responses={200: OpenApiResponse(description='Skill gap analysis result')},
        description='Analyze skill gaps and get course recommendations',
    )
    def post(self, request):
        serializer = SkillGapSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_skills = serializer.validated_data['user_skills']
        target_skills = serializer.validated_data['target_skills']

        analysis = SkillGapAnalysis.analyze_skills(user_skills, target_skills)
        courses = SkillGapAnalysis.recommend_courses(analysis['missing_skills'])

        return Response({
            'success': True,
            'data': {
                'analysis': analysis,
                'course_recommendations': courses,
            },
        }, status=status.HTTP_200_OK)


@extend_schema(tags=['AI Features'])
class UpskillingView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UpskillingSerializer,
        responses={200: OpenApiResponse(description='Upskilling path suggestion')},
        description='Get step-by-step upskilling path for career goal',
    )
    def post(self, request):
        serializer = UpskillingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = SkillGapAnalysis.suggest_upskilling_path(
            serializer.validated_data['current_skills'],
            serializer.validated_data['career_goal'],
        )

        return Response({'success': True, 'data': result}, status=status.HTTP_200_OK)


@extend_schema(tags=['AI Features'])
class SalaryPredictionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SalaryPredictionSerializer,
        responses={200: OpenApiResponse(description='Salary prediction result')},
        description='Predict salary range for a job title',
    )
    def get(self, request):
        serializer = SalaryPredictionSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = SalaryPredictionService.predict_salary(
            serializer.validated_data['job_title'],
            serializer.validated_data.get('experience', 0),
            serializer.validated_data.get('city', ''),
            serializer.validated_data.get('skills', []),
        )

        return Response({'success': True, 'data': result}, status=status.HTTP_200_OK)


@extend_schema(tags=['AI Features'])
class CareerRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CareerRecommendationSerializer,
        responses={200: OpenApiResponse(description='Career recommendations')},
        description='Get career path recommendations based on profile',
    )
    def post(self, request):
        serializer = CareerRecommendationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_profile = {
            'skills': serializer.validated_data.get('skills', []),
            'experience_years': serializer.validated_data.get('experience_years', 0),
            'preferred_job_categories': serializer.validated_data.get('preferred_categories', []),
        }

        paths = CareerRecommendationService.recommend_career_paths(user_profile)
        next_roles = CareerRecommendationService.suggest_next_roles(
            serializer.validated_data.get('current_role', ''),
            serializer.validated_data.get('experience_years', 0),
        )

        return Response({
            'success': True,
            'data': {
                'recommended_paths': paths,
                'next_role_suggestions': next_roles,
            },
        }, status=status.HTTP_200_OK)


@extend_schema(tags=['AI Features'])
class JobRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=JobRecommendationSerializer,
        responses={200: OpenApiResponse(description='Personalized job recommendations')},
        description='Get personalized job recommendations',
    )
    def get(self, request):
        serializer = JobRecommendationSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        saved_jobs = None
        recent_views = None

        if hasattr(user, 'saved_jobs'):
            saved_jobs = user.saved_jobs.all()

        user_profile = {
            'skills': serializer.validated_data.get('skills', []),
            'preferred_job_categories': serializer.validated_data.get('preferred_categories', []),
            'preferred_locations': serializer.validated_data.get('preferred_locations', []),
            'city': serializer.validated_data.get('city', ''),
        }

        if not user_profile['skills'] and hasattr(user, 'employee_profile') and user.employee_profile:
            user_profile['skills'] = user.employee_profile.skills or []
            user_profile['preferred_job_categories'] = user.employee_profile.preferred_job_categories or []
            user_profile['preferred_locations'] = user.employee_profile.preferred_locations or []
            user_profile['city'] = user.employee_profile.city or ''

        recommendations = JobRecommendationEngine.recommend_jobs(user_profile, recent_views, saved_jobs)

        return Response({
            'success': True,
            'data': {
                'recommendations': recommendations,
                'total': len(recommendations),
            },
        }, status=status.HTTP_200_OK)


@extend_schema(tags=['AI Features'])
class FraudCheckView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=FraudCheckSerializer,
        responses={200: OpenApiResponse(description='Fraud check result')},
        description='Check for fraudulent jobs, duplicate jobs, spam applications',
    )
    def post(self, request):
        serializer = FraudCheckSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        check_type = serializer.validated_data['check_type']
        result = None

        if check_type == 'job':
            result = FraudDetectionService.detect_fraudulent_job({
                'title': serializer.validated_data.get('title', ''),
                'description': serializer.validated_data.get('description', ''),
                'company_name': serializer.validated_data.get('company_name', ''),
                'salary_min': serializer.validated_data.get('salary_min'),
                'salary_max': serializer.validated_data.get('salary_max'),
                'contact_email': serializer.validated_data.get('contact_email', ''),
            })

        elif check_type == 'duplicate':
            from jobs.models import Job
            title = serializer.validated_data.get('title', '')
            existing_jobs = Job.objects.filter(status='active')[:50]
            result = FraudDetectionService.detect_duplicate_jobs(
                {'title': title, 'description': serializer.validated_data.get('description', '')},
                existing_jobs,
            )

        elif check_type == 'application':
            result = FraudDetectionService.detect_spam_application({
                'cover_letter': serializer.validated_data.get('cover_letter', ''),
                'email': serializer.validated_data.get('email', ''),
                'phone': serializer.validated_data.get('phone', ''),
            })

        elif check_type == 'employer':
            result = FraudDetectionService.check_employer_verification(
                serializer.validated_data.get('employer_id', ''),
            )

        return Response({'success': True, 'data': result}, status=status.HTTP_200_OK)
