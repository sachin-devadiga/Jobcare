import time
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import VoiceSession
from .serializers import (
    VoiceSessionSerializer, SpeechToTextSerializer,
    TextToSpeechSerializer, VoiceSearchSerializer,
    ExtractProfileSerializer,
)
from .services import SarvamAIService
from .llm_service import LLMProfileExtractionService

logger = logging.getLogger('jobcare')
sarvam_ai_service = SarvamAIService()


@extend_schema(tags=['Voice AI'])
class SpeechToTextView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=SpeechToTextSerializer,
        responses={200: OpenApiResponse(description='Transcribed text')},
        description='Convert speech audio to text using Sarvam AI',
    )
    def post(self, request):
        serializer = SpeechToTextSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session = VoiceSession.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_type='speech_to_text',
            status='processing',
            audio_url=serializer.validated_data.get('audio_url', ''),
            input_text='',
        )

        try:
            result = sarvam_ai_service.speech_to_text(
                audio_url=serializer.validated_data.get('audio_url', ''),
                language=serializer.validated_data.get('language', 'hi'),
            )

            if result and result.get('text'):
                session.status = 'completed'
                session.output_text = result['text']
                session.detected_language = result.get('language', '')
                session.confidence_score = result.get('confidence')
                session.processing_time_ms = result.get('processing_time_ms')
                session.save()

                return Response(
                    {
                        'success': True,
                        'data': {
                            'text': result['text'],
                            'language': result.get('language', ''),
                            'confidence': result.get('confidence'),
                            'processing_time_ms': result.get('processing_time_ms'),
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                session.status = 'failed'
                session.error_message = 'Speech recognition failed'
                session.save()
                return Response(
                    {'success': False, 'message': 'Speech recognition failed'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        except Exception as e:
            session.status = 'failed'
            session.error_message = str(e)
            session.save()
            logger.error(f'STT error: {str(e)}', exc_info=True)
            return Response(
                {'success': False, 'message': 'Speech recognition error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(tags=['Voice AI'])
class TextToSpeechView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=TextToSpeechSerializer,
        responses={200: OpenApiResponse(description='Audio URL')},
        description='Convert text to speech using Sarvam AI',
    )
    def post(self, request):
        serializer = TextToSpeechSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session = VoiceSession.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_type='text_to_speech',
            status='processing',
            input_text=serializer.validated_data['text'],
        )

        try:
            result = sarvam_ai_service.text_to_speech(
                text=serializer.validated_data['text'],
                language=serializer.validated_data.get('language', 'hi'),
                voice=serializer.validated_data.get('voice', 'male'),
            )

            if result and result.get('audio_url'):
                session.status = 'completed'
                session.output_audio_url = result['audio_url']
                session.processing_time_ms = result.get('processing_time_ms')
                session.save()

                return Response(
                    {
                        'success': True,
                        'data': {
                            'audio_url': result['audio_url'],
                            'processing_time_ms': result.get('processing_time_ms'),
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                session.status = 'failed'
                session.error_message = 'Text to speech conversion failed'
                session.save()
                return Response(
                    {'success': False, 'message': 'Text to speech conversion failed'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        except Exception as e:
            session.status = 'failed'
            session.error_message = str(e)
            session.save()
            logger.error(f'TTS error: {str(e)}', exc_info=True)
            return Response(
                {'success': False, 'message': 'Text to speech error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(tags=['Voice AI'])
class VoiceSearchView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=VoiceSearchSerializer,
        responses={200: OpenApiResponse(description='Search results')},
        description='Voice-powered job search',
    )
    def post(self, request):
        serializer = VoiceSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = serializer.validated_data['query']
        language = serializer.validated_data.get('language', 'hi')

        session = VoiceSession.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_type='voice_search',
            status='processing',
            input_text=query,
            detected_language=language,
        )

        try:
            result = sarvam_ai_service.voice_search(query, language)
            session.status = 'completed'
            session.output_text = f'Found {result["results_count"]} jobs'
            session.save()

            return Response(
                {
                    'success': True,
                    'data': result,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            session.status = 'failed'
            session.error_message = str(e)
            session.save()
            logger.error(f'Voice search error: {str(e)}', exc_info=True)
            return Response(
                {'success': False, 'message': 'Voice search failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(tags=['Voice AI'])
class VoiceNavigationView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=VoiceSearchSerializer,
        responses={200: OpenApiResponse(description='Navigation instruction')},
        description='Process voice navigation commands',
    )
    def post(self, request):
        serializer = VoiceSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = serializer.validated_data['query']
        language = serializer.validated_data.get('language', 'hi')

        session = VoiceSession.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_type='voice_navigation',
            status='processing',
            input_text=query,
            detected_language=language,
        )

        try:
            result = sarvam_ai_service.process_voice_command(query, language)
            session.status = 'completed'
            session.output_text = result.get('message', '')
            session.metadata = result
            session.save()

            return Response(
                {'success': True, 'data': result},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            session.status = 'failed'
            session.error_message = str(e)
            session.save()
            logger.error(f'Voice navigation error: {str(e)}', exc_info=True)
            return Response(
                {'success': False, 'message': 'Voice navigation failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(tags=['Voice AI'])
class VoiceSessionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: VoiceSessionSerializer(many=True)},
        description='Get voice session history',
    )
    def get(self, request):
        sessions = VoiceSession.objects.filter(user=request.user).order_by('-created_at')
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))

        from django.core.paginator import Paginator
        paginator = Paginator(sessions, per_page)
        page_obj = paginator.get_page(page)

        serializer = VoiceSessionSerializer(page_obj.object_list, many=True)
        return Response(
            {
                'success': True,
                'data': {
                    'results': serializer.data,
                    'count': paginator.count,
                    'page': page,
                    'total_pages': paginator.num_pages,
                },
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Voice AI'])
class ExtractProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ExtractProfileSerializer,
        responses={200: OpenApiResponse(description='Extracted profile data')},
        description='Extract structured profile data from a voice transcript using LLM',
    )
    def post(self, request):
        serializer = ExtractProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transcript = serializer.validated_data['transcript']
        language = serializer.validated_data.get('language', 'hi')

        service = LLMProfileExtractionService()
        result = service.extract_profile(transcript, language)

        return Response(
            {'success': True, 'data': result},
            status=status.HTTP_200_OK,
        )
