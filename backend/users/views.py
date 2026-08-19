from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiResponse
import os
import uuid

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
            serializer = EmployeeProfileSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({'success': True, 'message': 'Profile created', 'data': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'success': False, 'message': 'Validation failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
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
class ProfileAvatarUploadView(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        avatar = request.FILES.get('avatar') or request.FILES.get('image')
        if not avatar:
            return Response({'success': False, 'message': 'An avatar image is required'}, status=status.HTTP_400_BAD_REQUEST)
        profile = repo.get_by_user(user_id=request.user.id)
        if not profile:
            return Response({'success': False, 'message': 'Create your profile before uploading an avatar'}, status=status.HTTP_404_NOT_FOUND)
        profile.avatar = avatar
        profile.save()
        return Response({'success': True, 'data': EmployeeProfileSerializer(profile, context={'request': request}).data})


@extend_schema(tags=['Users'])
class ProfileVoiceResumeUploadView(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        from django.core.files.storage import default_storage
        audio = request.FILES.get('voice_resume')
        resume = request.FILES.get('resume') or request.FILES.get('file')
        if not audio and not resume:
            return Response(
                {'success': False, 'message': 'A voice resume or resume file is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile = repo.get_by_user(user_id=request.user.id)
        if not profile:
            profile_serializer = EmployeeProfileSerializer(data={}, context={'request': request})
            profile_serializer.is_valid(raise_exception=True)
            profile = profile_serializer.save()
        if audio:
            ext = os.path.splitext(audio.name)[1] or '.m4a'
            path = default_storage.save(f'voice_resumes/{uuid.uuid4()}{ext}', audio)
            url = request.build_absolute_uri(default_storage.url(path))
            profile.voice_resume_url = url
        if resume:
            ext = os.path.splitext(resume.name)[1] or '.pdf'
            path = default_storage.save(f'resumes/{uuid.uuid4()}{ext}', resume)
            url = request.build_absolute_uri(default_storage.url(path))
            profile.resume_url = url
        profile.save(update_fields=['voice_resume_url', 'resume_url'])
        return Response(
            {'success': True, 'data': {'voice_resume_url': profile.voice_resume_url, 'resume_url': profile.resume_url}},
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        profile = repo.get_by_user(user_id=request.user.id)
        if profile:
            profile.voice_resume_url = ''
            profile.resume_url = ''
            profile.save(update_fields=['voice_resume_url', 'resume_url'])
        return Response(
            {'success': True, 'message': 'Resumes deleted'},
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
