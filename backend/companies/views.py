from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from drf_spectacular.utils import extend_schema, OpenApiResponse

from authentication.permissions import IsEmployer, IsAdmin
from .models import Company
from .serializers import (
    CompanySerializer, CompanyListSerializer, CompanyVerifySerializer,
)
from .repositories.company_repository import CompanyRepository

repo = CompanyRepository()


@extend_schema(tags=['Companies'])
class CompanyListCreateView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        responses={200: CompanyListSerializer(many=True)},
        description='List all companies',
    )
    def get(self, request):
        companies = repo.all()
        filter_backend = DjangoFilterBackend()
        filtered = filter_backend.filter_queryset(request, companies, self)
        search_filter = SearchFilter()
        searched = search_filter.filter_queryset(request, filtered, self)

        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))
        result = repo.paginate(searched, page=page, per_page=per_page)

        serializer = CompanyListSerializer(result['results'], many=True)
        result['results'] = serializer.data
        return Response({'success': True, 'data': result}, status=status.HTTP_200_OK)

    @extend_schema(
        request=CompanySerializer,
        responses={201: CompanySerializer},
        description='Create a new company',
    )
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'success': False, 'message': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if request.user.role not in ['employer', 'admin']:
            return Response(
                {'success': False, 'message': 'Only employers can create companies'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = CompanySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(
            {'success': True, 'message': 'Company created', 'data': serializer.data},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['Companies'])
class CompanyDetailView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        return repo.get_by_id(pk)

    @extend_schema(
        responses={200: CompanySerializer},
        description='Get company details',
    )
    def get(self, request, pk):
        company = self.get_object(pk)
        if not company:
            return Response(
                {'success': False, 'message': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CompanySerializer(company)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        request=CompanySerializer,
        responses={200: CompanySerializer},
        description='Update company',
    )
    def patch(self, request, pk):
        if not request.user.is_authenticated:
            return Response(
                {'success': False, 'message': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        company = self.get_object(pk)
        if not company:
            return Response(
                {'success': False, 'message': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CompanySerializer(company, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(
            {'success': True, 'message': 'Company updated', 'data': serializer.data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={200: OpenApiResponse(description='Company deleted')},
        description='Delete company',
    )
    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return Response(
                {'success': False, 'message': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        company = self.get_object(pk)
        if not company:
            return Response(
                {'success': False, 'message': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        company.delete()
        return Response(
            {'success': True, 'message': 'Company deleted'},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Companies'])
class CompanyVerifyView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        request=CompanyVerifySerializer,
        responses={200: CompanySerializer},
        description='Verify or reject a company (admin)',
    )
    def post(self, request, pk):
        company = repo.get_by_id(pk)
        if not company:
            return Response(
                {'success': False, 'message': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CompanyVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        company.verification_status = serializer.validated_data['status']
        company.save(update_fields=['verification_status'])
        company_serializer = CompanySerializer(company)
        return Response(
            {'success': True, 'message': f'Company {serializer.validated_data["status"]}', 'data': company_serializer.data},
            status=status.HTTP_200_OK,
        )
