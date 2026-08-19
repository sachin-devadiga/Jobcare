import time
import logging
import base64
import uuid
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import VoiceSession
from .serializers import (
    VoiceSessionSerializer, SpeechToTextSerializer,
    TextToSpeechSerializer, VoiceSearchSerializer,
    ExtractProfileSerializer, BuildResumeSerializer,
)
from .services import SarvamAIService
from .llm_service import LLMProfileExtractionService

logger = logging.getLogger('jobcare')
sarvam_ai_service = SarvamAIService()


def _looks_like_synthetic_tone(audio_path, silence_fraction_limit=0.04):
    """Detect recordings with essentially no silence (e.g. the emulator's virtual-mic tone).

    Real speech always contains pauses; a periodic synthetic tone does not.
    Returns True when the audio is almost entirely non-silent, so callers can
    reject it instead of feeding it to STT (which may hallucinate text from tones).
    """
    try:
        import av as _av
        import audioop as _audioop
        container = _av.open(audio_path)
        stream = container.streams.audio[0]
        rate = stream.codec_context.sample_rate
        raw = b''
        for frame in container.decode(stream):
            raw += bytes(frame.planes[0])
        container.close()
        if not raw:
            return False
        win = max(1, rate // 10)
        frames = len(raw) // (2 * win)
        if frames < 10:
            return False
        silent = 0
        for i in range(0, frames * win * 2, win * 2):
            if _audioop.rms(raw[i:i + win * 2], 2) < 800:
                silent += 1
        return (silent / frames) < silence_fraction_limit
    except Exception:
        logger.warning('Tone check skipped for %s', audio_path, exc_info=True)
        return False


@extend_schema(tags=['Voice AI'])
class SpeechToTextView(APIView):
    permission_classes = [IsAuthenticated]

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
            audio_input=serializer.validated_data['audio'],
            input_text='',
        )

        try:
            if _looks_like_synthetic_tone(session.audio_input.path):
                session.status = 'failed'
                session.error_message = 'No speech detected in the audio (microphone may not be connected)'
                session.save()
                return Response(
                    {'success': False, 'message': 'No speech was recognized. Please speak clearly and try again.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            result = sarvam_ai_service.speech_to_text(
                audio_file=serializer.validated_data['audio'],
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
                session.error_message = 'No speech was recognized in the audio'
                session.save()
                return Response(
                    {'success': False, 'message': 'No speech was recognized. Please speak clearly and try again.'},
                    status=status.HTTP_400_BAD_REQUEST,
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
    permission_classes = [IsAuthenticated]

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
            user=request.user,
            session_type='text_to_speech',
            status='processing',
            input_text=serializer.validated_data['text'],
        )

        try:
            result = sarvam_ai_service.text_to_speech(
                text=serializer.validated_data['text'],
                language=serializer.validated_data.get('language', 'hi'),
                voice=serializer.validated_data.get('voice', 'male'),
                pace=serializer.validated_data.get('pace', 1.0),
            )

            if result and result.get('audio_content'):
                try:
                    audio = base64.b64decode(result['audio_content'], validate=True)
                except (ValueError, TypeError) as exc:
                    raise ValueError('Voice provider returned invalid audio data') from exc
                path = default_storage.save(
                    f'voice_tts/{uuid.uuid4()}.mp3',
                    ContentFile(audio),
                )
                audio_url = request.build_absolute_uri(default_storage.url(path))
                session.status = 'completed'
                session.output_audio_url = audio_url
                session.processing_time_ms = result.get('processing_time_ms')
                session.save()

                return Response(
                    {
                        'success': True,
                        'data': {
                            'audio_url': audio_url,
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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
        try:
            page = max(1, int(request.query_params.get('page', 1)))
            per_page = min(100, max(1, int(request.query_params.get('per_page', 20))))
        except ValueError:
            return Response(
                {'success': False, 'message': 'page and per_page must be integers'},
                status=status.HTTP_400_BAD_REQUEST,
            )

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


@extend_schema(tags=['Voice AI'])
class BuildResumeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=BuildResumeSerializer,
        responses={200: OpenApiResponse(description='Built resume profile')},
        description='Upload voice audio → STT → extract profile → save to EmployeeProfile in one step',
    )
    def post(self, request):
        serializer = BuildResumeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session = VoiceSession.objects.create(
            user=request.user,
            session_type='speech_to_text',
            status='processing',
            audio_input=serializer.validated_data['audio'],
            input_text='',
        )

        try:
            if _looks_like_synthetic_tone(session.audio_input.path):
                session.status = 'failed'
                session.error_message = 'No speech detected'
                session.save()
                return Response(
                    {'success': False, 'message': 'No speech was recognized. Please speak clearly and try again.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            stt_result = sarvam_ai_service.speech_to_text(
                audio_file=serializer.validated_data['audio'],
                language=serializer.validated_data.get('language', 'hi'),
            )

            transcript = stt_result.get('text', '') if stt_result else ''
            if not transcript:
                session.status = 'failed'
                session.error_message = 'No speech was recognized'
                session.save()
                return Response(
                    {'success': False, 'message': 'No speech was recognized. Please speak clearly and try again.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            session.output_text = transcript
            session.detected_language = stt_result.get('language', '')
            session.confidence_score = stt_result.get('confidence')

            llm_service = LLMProfileExtractionService()
            profile_data = llm_service.extract_profile(transcript, serializer.validated_data.get('language', 'hi'))

            from users.models import EmployeeProfile
            profile, _ = EmployeeProfile.objects.get_or_create(
                user=request.user,
                defaults={'full_name': request.user.get_full_name() or request.user.email.split('@')[0]},
            )

            if profile_data.get('skills'):
                existing_skills = profile.skills or []
                for s in profile_data['skills']:
                    if s not in existing_skills:
                        existing_skills.append(s)
                profile.skills = existing_skills

            if profile_data.get('experience_years'):
                new_years = profile_data['experience_years']
                if new_years > (profile.experience_years or 0):
                    profile.experience_years = new_years

            if profile_data.get('education'):
                existing_edu = profile.education or []
                new_edu_keys = {(e.get('degree', ''), e.get('field', '')) for e in profile_data['education']}
                for e in profile_data['education']:
                    key = (e.get('degree', ''), e.get('field', ''))
                    if key not in {(x.get('degree', ''), x.get('field', '')) for x in existing_edu}:
                        existing_edu.append(e)
                profile.education = existing_edu

            if profile_data.get('languages'):
                existing_langs = profile.languages or []
                for lang in profile_data['languages']:
                    if lang not in existing_langs:
                        existing_langs.append(lang)
                profile.languages = existing_langs

            if profile_data.get('certificates'):
                existing_certs = profile.certificates or []
                for c in profile_data['certificates']:
                    if c.get('name') not in [x.get('name') for x in existing_certs]:
                        existing_certs.append(c)
                profile.certificates = existing_certs

            profile.save()

            session.status = 'completed'
            session.metadata = profile_data
            session.save()

            return Response(
                {
                    'success': True,
                    'data': {
                        'transcript': transcript,
                        'language': stt_result.get('language', ''),
                        'profile': {
                            'skills': profile.skills,
                            'experience_years': float(profile.experience_years),
                            'education': profile.education,
                            'languages': profile.languages,
                            'certificates': profile.certificates,
                        },
                        'profile_completion_score': profile.profile_completion_score,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            session.status = 'failed'
            session.error_message = str(e)
            session.save()
            logger.error(f'Build resume error: {str(e)}', exc_info=True)
            return Response(
                {'success': False, 'message': f'Failed to build resume: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
