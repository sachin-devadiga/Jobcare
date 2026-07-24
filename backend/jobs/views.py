from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from authentication.permissions import IsEmployer, IsAdmin
from .models import Job, Category, Skill, City
from .serializers import (
    JobListSerializer, JobDetailSerializer, JobCreateUpdateSerializer,
    CategorySerializer, SkillSerializer, CitySerializer,
)
from .repositories.job_repository import JobRepository

repo = JobRepository()


@extend_schema(tags=['Jobs'])
class JobListCreateView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='search', description='Search by title, description, company, city', type=str),
            OpenApiParameter(name='job_type', description='Filter by job type', type=str),
            OpenApiParameter(name='city', description='Filter by city', type=str),
            OpenApiParameter(name='state', description='Filter by state', type=str),
            OpenApiParameter(name='category', description='Filter by category ID', type=str),
            OpenApiParameter(name='experience_min', description='Minimum experience', type=int),
            OpenApiParameter(name='salary_min', description='Minimum salary', type=int),
            OpenApiParameter(name='salary_max', description='Maximum salary', type=int),
            OpenApiParameter(name='is_featured', description='Featured jobs', type=bool),
            OpenApiParameter(name='ordering', description='Order by field', type=str),
            OpenApiParameter(name='page', description='Page number', type=int),
            OpenApiParameter(name='per_page', description='Items per page', type=int),
        ],
        responses={200: JobListSerializer(many=True)},
        description='List jobs with filtering, search, and pagination',
    )
    def get(self, request):
        queryset = repo.get_active_jobs()

        filter_backend = DjangoFilterBackend()
        filter_backend.filterset_fields = {
            'job_type': ['exact'],
            'city': ['exact', 'icontains'],
            'state': ['exact', 'icontains'],
            'category': ['exact'],
            'is_featured': ['exact'],
            'is_urgent': ['exact'],
            'salary_min': ['gte'],
            'salary_max': ['lte'],
            'experience_min': ['gte'],
            'experience_max': ['lte'],
            'urgency': ['exact'],
            'shift_timing': ['exact'],
        }
        queryset = filter_backend.filter_queryset(request, queryset, self)

        search_filter = SearchFilter()
        search_filter.search_fields = ['title', 'description', 'company__name', 'city', 'state', 'skills_required']
        queryset = search_filter.filter_queryset(request, queryset, self)

        ordering_filter = OrderingFilter()
        ordering_filter.ordering_fields = ['created_at', 'salary_min', 'experience_min', 'views_count', 'application_count']
        queryset = ordering_filter.filter_queryset(request, queryset, self)

        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))
        result = repo.paginate(queryset, page=page, per_page=per_page)

        serializer = JobListSerializer(result['results'], many=True)
        result['results'] = serializer.data
        return Response({'success': True, 'data': result}, status=status.HTTP_200_OK)

    @extend_schema(
        request=JobCreateUpdateSerializer,
        responses={201: JobDetailSerializer},
        description='Create a new job posting',
    )
    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_employer:
            return Response(
                {'success': False, 'message': 'Only employers can post jobs'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = JobCreateUpdateSerializer(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(
            {'success': True, 'message': 'Job posted successfully', 'data': serializer.data},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['Jobs'])
class JobDetailView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return repo.get_by_id(pk)

    @extend_schema(
        responses={200: JobDetailSerializer},
        description='Get job details',
    )
    def get(self, request, pk):
        job = self.get_object(pk)
        if not job:
            return Response(
                {'success': False, 'message': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        repo.increment_views(job.id)
        serializer = JobDetailSerializer(job)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        request=JobCreateUpdateSerializer,
        responses={200: JobDetailSerializer},
        description='Update job posting',
    )
    def patch(self, request, pk):
        if not request.user.is_authenticated:
            return Response(
                {'success': False, 'message': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        job = self.get_object(pk)
        if not job:
            return Response(
                {'success': False, 'message': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.user != job.employer and not request.user.is_admin_user:
            return Response(
                {'success': False, 'message': 'Not authorized to edit this job'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = JobCreateUpdateSerializer(
            job, data=request.data, partial=True,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(
            {'success': True, 'message': 'Job updated', 'data': serializer.data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={200: OpenApiResponse(description='Job deleted')},
        description='Delete job posting',
    )
    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return Response(
                {'success': False, 'message': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        job = self.get_object(pk)
        if not job:
            return Response(
                {'success': False, 'message': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.user != job.employer and not request.user.is_admin_user:
            return Response(
                {'success': False, 'message': 'Not authorized to delete this job'},
                status=status.HTTP_403_FORBIDDEN,
            )
        job.delete()
        return Response(
            {'success': True, 'message': 'Job deleted'},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Jobs'])
class NearbyJobsView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='latitude', required=True, type=float),
            OpenApiParameter(name='longitude', required=True, type=float),
            OpenApiParameter(name='radius', description='Radius in km (default: 25)', type=float),
        ],
        responses={200: JobListSerializer(many=True)},
        description='Find jobs near a location',
    )
    def get(self, request):
        try:
            latitude = float(request.query_params.get('latitude', 0))
            longitude = float(request.query_params.get('longitude', 0))
            radius = float(request.query_params.get('radius', 25))

            if not latitude or not longitude:
                return Response(
                    {'success': False, 'message': 'Latitude and longitude are required'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            jobs = repo.get_nearby_jobs(latitude, longitude, radius)
            page = int(request.query_params.get('page', 1))
            per_page = int(request.query_params.get('per_page', 20))
            result = repo.paginate(jobs, page=page, per_page=per_page)
            serializer = JobListSerializer(result['results'], many=True)
            result['results'] = serializer.data
            return Response({'success': True, 'data': result}, status=status.HTTP_200_OK)
        except (ValueError, TypeError):
            return Response(
                {'success': False, 'message': 'Invalid coordinates'},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(tags=['Jobs'])
class EmployerJobListView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    @extend_schema(
        responses={200: JobListSerializer(many=True)},
        description='List jobs posted by current employer',
    )
    def get(self, request):
        jobs = repo.get_by_employer(request.user.id)
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))
        result = repo.paginate(jobs, page=page, per_page=per_page)
        serializer = JobListSerializer(result['results'], many=True)
        result['results'] = serializer.data
        return Response({'success': True, 'data': result}, status=status.HTTP_200_OK)


@extend_schema(tags=['Jobs'])
class JobStatusView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description='Job status updated')},
        description='Update job status (active/paused/closed/filled)',
    )
    def patch(self, request, pk):
        job = repo.get_by_id(pk)
        if not job:
            return Response(
                {'success': False, 'message': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.user != job.employer:
            return Response(
                {'success': False, 'message': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN,
            )
        new_status = request.data.get('status')
        if new_status not in ['active', 'paused', 'closed', 'filled']:
            return Response(
                {'success': False, 'message': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        job.status = new_status
        job.save(update_fields=['status'])
        return Response(
            {'success': True, 'message': f'Job status updated to {new_status}'},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Jobs'])
class CategoryListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: CategorySerializer(many=True)},
        description='List all job categories',
    )
    def get(self, request):
        categories = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
        serializer = CategorySerializer(categories, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


@extend_schema(tags=['Jobs'])
class SkillListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: SkillSerializer(many=True)},
        description='List all skills',
    )
    def get(self, request):
        skills = Skill.objects.filter(is_active=True)
        category_id = request.query_params.get('category')
        if category_id:
            skills = skills.filter(category_id=category_id)
        serializer = SkillSerializer(skills, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


@extend_schema(tags=['Jobs'])
class CityListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: CitySerializer(many=True)},
        description='List all cities',
    )
    def get(self, request):
        cities = City.objects.filter(is_active=True)
        state = request.query_params.get('state')
        if state:
            cities = cities.filter(state__iexact=state)
        serializer = CitySerializer(cities, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
