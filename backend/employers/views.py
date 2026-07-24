from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from authentication.permissions import IsEmployer, IsAdmin
from .models import EmployerProfile
from .serializers import EmployerProfileSerializer, EmployerProfileListSerializer
from .repositories.employer_profile_repository import EmployerProfileRepository

repo = EmployerProfileRepository()


@extend_schema(tags=['Employers'])
class EmployerProfileView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    @extend_schema(
        responses={200: EmployerProfileSerializer},
        description='Get current employer profile',
    )
    def get(self, request):
        profile = repo.get_by_user(user_id=request.user.id)
        if not profile:
            return Response(
                {'success': False, 'message': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = EmployerProfileSerializer(profile, context={'request': request})
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        request=EmployerProfileSerializer,
        responses={201: EmployerProfileSerializer},
        description='Create employer profile',
    )
    def post(self, request):
        if repo.get_by_user(user_id=request.user.id):
            return Response(
                {'success': False, 'message': 'Profile already exists. Use PATCH to update.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = EmployerProfileSerializer(
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
        request=EmployerProfileSerializer,
        responses={200: EmployerProfileSerializer},
        description='Update employer profile',
    )
    def patch(self, request):
        profile = repo.get_by_user(user_id=request.user.id)
        if not profile:
            return Response(
                {'success': False, 'message': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = EmployerProfileSerializer(
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


@extend_schema(tags=['Employers'])
class EmployerProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: EmployerProfileSerializer},
        description='Get employer profile by ID',
    )
    def get(self, request, pk):
        profile = repo.get_by_id(pk)
        if not profile:
            return Response(
                {'success': False, 'message': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = EmployerProfileSerializer(profile, context={'request': request})
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


@extend_schema(tags=['Employers'])
class EmployerProfileListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        responses={200: EmployerProfileListSerializer(many=True)},
        description='List all employer profiles (admin)',
    )
    def get(self, request):
        profiles = repo.all()
        serializer = EmployerProfileListSerializer(profiles, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
