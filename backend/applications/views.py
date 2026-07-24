from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from authentication.permissions import IsEmployee, IsEmployer, IsAdmin, IsOwnerOrAdmin
from .models import Application
from .serializers import (
    ApplicationSerializer, ApplicationCreateSerializer,
    ApplicationUpdateSerializer, ApplicationDetailSerializer,
    ApplicationStatusSerializer,
)
from .repositories.application_repository import ApplicationRepository
from .services import AIMatchScoreService
from jobs.repositories.job_repository import JobRepository

repo = ApplicationRepository()
job_repo = JobRepository()
ai_service = AIMatchScoreService()


@extend_schema(tags=['Applications'])
class ApplyForJobView(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    @extend_schema(
        request=ApplicationCreateSerializer,
        responses={201: ApplicationSerializer},
        description='Apply for a job',
    )
    def post(self, request):
        serializer = ApplicationCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        application = serializer.save()

        job_repo.increment_applications(application.job.id)

        try:
            ai_service.calculate_and_save(application)
        except Exception as e:
            pass

        result_serializer = ApplicationSerializer(application)
        return Response(
            {'success': True, 'message': 'Application submitted', 'data': result_serializer.data},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['Applications'])
class MyApplicationsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='status', description='Filter by status', type=str),
            OpenApiParameter(name='page', type=int),
        ],
        responses={200: ApplicationDetailSerializer(many=True)},
        description='Get my job applications',
    )
    def get(self, request):
        if request.user.is_employee:
            applications = repo.get_by_employee(request.user.id)
        elif request.user.is_employer:
            applications = repo.get_by_employer(request.user.id)
        else:
            applications = repo.all()

        status_filter = request.query_params.get('status')
        if status_filter:
            applications = applications.filter(status=status_filter)

        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))
        result = repo.paginate(applications, page=page, per_page=per_page)

        serializer = ApplicationDetailSerializer(result['results'], many=True)
        result['results'] = serializer.data
        return Response({'success': True, 'data': result}, status=status.HTTP_200_OK)


@extend_schema(tags=['Applications'])
class ApplicationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Application.objects.select_related(
                'job', 'employee', 'employee__employee_profile'
            ).get(id=pk)
        except Application.DoesNotExist:
            return None

    @extend_schema(
        responses={200: ApplicationDetailSerializer},
        description='Get application details',
    )
    def get(self, request, pk):
        application = self.get_object(pk)
        if not application:
            return Response(
                {'success': False, 'message': 'Application not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not self._can_access(request.user, application):
            return Response(
                {'success': False, 'message': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ApplicationDetailSerializer(application)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def _can_access(self, user, application):
        if user.is_admin_user:
            return True
        if user == application.employee:
            return True
        if user == application.job.employer:
            return True
        return False


@extend_schema(tags=['Applications'])
class ApplicationStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def get_object(self, pk):
        try:
            return Application.objects.select_related('job', 'employee').get(id=pk)
        except Application.DoesNotExist:
            return None

    @extend_schema(
        request=ApplicationStatusSerializer,
        responses={200: ApplicationDetailSerializer},
        description='Update application status (employer only)',
    )
    def patch(self, request, pk):
        application = self.get_object(pk)
        if not application:
            return Response(
                {'success': False, 'message': 'Application not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.user != application.job.employer and not request.user.is_admin_user:
            return Response(
                {'success': False, 'message': 'Not authorized to update this application'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ApplicationStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.status = serializer.validated_data['status']
        if 'employer_notes' in request.data:
            application.employer_notes = request.data.get('employer_notes', '')
        if serializer.validated_data.get('rejection_reason'):
            application.rejection_reason = serializer.validated_data['rejection_reason']
        application.save()

        result_serializer = ApplicationDetailSerializer(application)
        return Response(
            {'success': True, 'message': f'Application status updated to {application.get_status_display()}',
             'data': result_serializer.data},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Applications'])
class ApplicationInterviewView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def get_object(self, pk):
        try:
            return Application.objects.get(id=pk)
        except Application.DoesNotExist:
            return None

    @extend_schema(
        request=None,
        responses={200: ApplicationDetailSerializer},
        description='Schedule interview for applicant',
    )
    def post(self, request, pk):
        application = self.get_object(pk)
        if not application:
            return Response(
                {'success': False, 'message': 'Application not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.user != application.job.employer:
            return Response(
                {'success': False, 'message': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN,
            )

        application.interview_date = request.data.get('interview_date')
        application.interview_time = request.data.get('interview_time')
        application.interview_location = request.data.get('interview_location', '')
        application.interview_type = request.data.get('interview_type')
        application.status = 'interview_scheduled'
        application.save()

        serializer = ApplicationDetailSerializer(application)
        return Response(
            {'success': True, 'message': 'Interview scheduled', 'data': serializer.data},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Applications'])
class WithdrawApplicationView(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def post(self, request, pk):
        application = repo.get_by_id(pk)
        if not application:
            return Response(
                {'success': False, 'message': 'Application not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.user != application.employee:
            return Response(
                {'success': False, 'message': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if application.status in ['selected', 'offered', 'hired', 'rejected']:
            return Response(
                {'success': False, 'message': f'Cannot withdraw a {application.status} application'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.status = 'withdrawn'
        application.save(update_fields=['status'])

        return Response(
            {'success': True, 'message': 'Application withdrawn'},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Applications'])
class JobApplicationsView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='status', type=str),
            OpenApiParameter(name='page', type=int),
        ],
        responses={200: ApplicationDetailSerializer(many=True)},
        description='Get all applications for a specific job',
    )
    def get(self, request, job_id):
        from jobs.models import Job
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.user != job.employer and not request.user.is_admin_user:
            return Response(
                {'success': False, 'message': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN,
            )

        applications = repo.get_applications_for_job(job_id)
        status_filter = request.query_params.get('status')
        if status_filter:
            applications = applications.filter(status=status_filter)

        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))
        result = repo.paginate(applications, page=page, per_page=per_page)

        serializer = ApplicationDetailSerializer(result['results'], many=True)
        result['results'] = serializer.data
        return Response({'success': True, 'data': result}, status=status.HTTP_200_OK)
