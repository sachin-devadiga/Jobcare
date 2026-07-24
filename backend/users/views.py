from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiResponse

from authentication.permissions import IsEmployee, IsOwnerOrAdmin
from .models import EmployeeProfile
from .serializers import (
    EmployeeProfileSerializer, EmployeeProfileListSerializer,
    AadhaarVerificationSerializer,
)
from .repositories.employee_profile_repository import EmployeeProfileRepository

repo = EmployeeProfileRepository()


@extend_schema(tags=['Users'])
class EmployeeProfileView(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        responses={200: EmployeeProfileSerializer},
        description='Get current employee profile',
    )
    def get(self, request):
        profile = repo.get_by_user(user_id=request.user.id)
        if not profile:
            return Response(
                {'success': False, 'message': 'Profile not found. Please create your profile.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = EmployeeProfileSerializer(profile, context={'request': request})
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        request=EmployeeProfileSerializer,
        responses={201: EmployeeProfileSerializer, 400: OpenApiResponse(description='Validation error')},
        description='Create employee profile',
    )
    def post(self, request):
        if repo.get_by_user(user_id=request.user.id):
            return Response(
                {'success': False, 'message': 'Profile already exists. Use PATCH to update.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = EmployeeProfileSerializer(
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
            {'success': True, 'message': 'Profile created', 'data': serializer.data},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        request=EmployeeProfileSerializer,
        responses={200: EmployeeProfileSerializer},
        description='Update employee profile',
    )
    def patch(self, request):
        profile = repo.get_by_user(user_id=request.user.id)
        if not profile:
            return Response(
                {'success': False, 'message': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = EmployeeProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(
            {'success': True, 'message': 'Profile updated', 'data': serializer.data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={200: OpenApiResponse(description='Profile deleted')},
        description='Delete employee profile',
    )
    def delete(self, request):
        profile = repo.get_by_user(user_id=request.user.id)
        if not profile:
            return Response(
                {'success': False, 'message': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        profile.delete()
        return Response(
            {'success': True, 'message': 'Profile deleted'},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Users'])
class EmployeeProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: EmployeeProfileSerializer},
        description='Get employee profile by ID',
    )
    def get(self, request, pk):
        profile = repo.get_by_id(pk)
        if not profile:
            return Response(
                {'success': False, 'message': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = EmployeeProfileSerializer(profile, context={'request': request})
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


@extend_schema(tags=['Users'])
class ProfileCompletionView(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    @extend_schema(
        responses={200: OpenApiResponse(description='Profile completion score')},
        description='Get profile completion score',
    )
    def get(self, request):
        profile = repo.get_by_user(user_id=request.user.id)
        if not profile:
            return Response(
                {'success': False, 'message': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        score = profile.calculate_completion_score()
        profile.save(update_fields=['profile_completion_score', 'is_profile_complete'])
        return Response(
            {
                'success': True,
                'data': {
                    'profile_completion_score': score,
                    'is_profile_complete': profile.is_profile_complete,
                },
            },
            status=status.HTTP_200_OK,
        )
