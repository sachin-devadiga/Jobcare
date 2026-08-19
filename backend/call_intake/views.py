import logging
import secrets
from io import BytesIO
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import requests
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import CallSession, IntakeQuestion, CallAnswer
from .services import IntakeVoiceService, normalize_language_code
from .tasks import process_completed_intake
from voice_ai.services import SarvamAIService

logger = logging.getLogger('jobcare')


class ExotelWebhookAuthenticationMixin:
    """Require the shared secret configured in the Exotel webhook URL/header."""

    def _is_authorized(self, request):
        configured = settings.EXOTEL_WEBHOOK_TOKEN
        supplied = request.headers.get('X-Exotel-Webhook-Token') or request.query_params.get('token', '')
        return bool(configured) and secrets.compare_digest(configured, supplied)

    def _reject_if_unauthorized(self, request):
        if not settings.EXOTEL_WEBHOOK_TOKEN:
            logger.critical('Exotel webhook rejected because EXOTEL_WEBHOOK_TOKEN is not configured')
            return HttpResponse('service_unavailable', status=503)
        if not self._is_authorized(request):
            logger.warning('Rejected unauthenticated Exotel webhook request')
            return HttpResponse('forbidden', status=403)
        return None

class ExotelIVRWebhookView(ExotelWebhookAuthenticationMixin, APIView):
    """
    The 'Brain' of the IVR. Exotel Passthru applets call this to get the next step.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        rejection = self._reject_if_unauthorized(request)
        if rejection:
            return rejection
        call_sid = request.POST.get('CallSid')
        from_number = request.POST.get('From')
        digits = request.POST.get('Digits')
        recording_url = request.POST.get('RecordingUrl')

        if not call_sid:
            return HttpResponse("error_no_sid")

        # 1. Get or Create Session
        session, _ = CallSession.objects.get_or_create(
            provider_call_sid=call_sid,
            defaults={'phone_number': from_number or 'unknown', 'status': CallSession.Status.IN_PROGRESS}
        )

        # 2. State: Language Selection
        if session.current_question_index == 0:
            if not digits:
                return HttpResponse("ask_language")
            
            lang_map = {'1': 'hindi', '2': 'kannada', '3': 'tamil'}
            session.language = lang_map.get(digits, 'hindi')
            session.current_question_index = 1
            session.save()
            return HttpResponse("start_questions")

        # 3. State: Processing an Answer (came from Record applet)
        questions = IntakeQuestion.objects.filter(is_active=True).order_by('order')
        
        # Ensure we don't go out of bounds
        if session.current_question_index > len(questions):
            return self._complete_call(session)

        current_q = questions[session.current_question_index - 1]

        if recording_url:
            return self._handle_recording(session, current_q, questions, recording_url)

        # 4. State: Handling Confirmation (came from Gather applet)
        if digits and (digits == '1' or digits == '2'):
            return self._handle_confirmation(session, current_q, questions, digits)

        # 5. Default: If we are within questions, play the current one
        if session.current_question_index <= len(questions):
            return HttpResponse("play_question")
        
        return self._complete_call(session)

    def _handle_recording(self, session, current_q, questions, recording_url):
        # Transcribe via Sarvam
        sarvam = SarvamAIService()
        # Sarvam STT returns native Unicode script (Hindi/Kannada/Tamil)
        stt_res = sarvam.speech_to_text(audio_url=recording_url, language=normalize_language_code(session.language))
        transcript = stt_res.get('text', '')

        if not transcript:
            return HttpResponse("retry_recording") # Optional: handle empty STT

        CallAnswer.objects.update_or_create(
            session=session,
            question=current_q,
            defaults={
                'answer_text': transcript,
                'audio_recording_url': recording_url,
                'answered_at': timezone.now(),
                'confirmed': False
            }
        )

        # Force confirmation for name and location specifically
        if current_q.question_key in ['name', 'location']:
            return HttpResponse("confirm_answer")
        
        # Auto-advance for other fields
        session.current_question_index += 1
        session.save()
        
        if session.current_question_index > len(questions):
            return self._complete_call(session)
            
        return HttpResponse("next_question")

    def _handle_confirmation(self, session, current_q, questions, digits):
        answer = CallAnswer.objects.filter(session=session, question=current_q).first()

        if digits == '1': # Confirmed
            if answer:
                answer.confirmed = True
                answer.save()
            session.current_question_index += 1
            session.save()
            
            if session.current_question_index > len(questions):
                return self._complete_call(session)
            return HttpResponse("next_question")
        else: # Retry (Digits == '2')
            return HttpResponse("retry_recording")

    def _complete_call(self, session):
        if session.status != CallSession.Status.COMPLETED:
            session.status = CallSession.Status.COMPLETED
            session.completed_at = timezone.now()
            session.save()
            # Trigger Phase 3: Background PDF generation and notification
            process_completed_intake.delay(str(session.id))
            
        return HttpResponse("thank_you")

class ServeQuestionAudioView(ExotelWebhookAuthenticationMixin, APIView):
    """
    Serves the audio file URL for the Play applet.
    Exotel calls this to know what to play next.
    """
    permission_classes = [AllowAny]

    def get(self, request, session_id):
        rejection = self._reject_if_unauthorized(request)
        if rejection:
            return rejection
        try:
            session = CallSession.objects.get(id=session_id)
            service = IntakeVoiceService()
            questions = IntakeQuestion.objects.filter(is_active=True).order_by('order')
            
            # Check if we are in confirmation mode for the last recorded answer
            # We look for an unconfirmed answer that requires confirmation
            last_answer = CallAnswer.objects.filter(session=session).order_by('-answered_at').first()
            if last_answer and not last_answer.confirmed and last_answer.question.question_key in ['name', 'location']:
                audio_url = service.get_confirmation_audio_url(last_answer.answer_text, session.language)
                return HttpResponseRedirect(audio_url)

            # Normal question path
            if session.current_question_index > 0 and session.current_question_index <= len(questions):
                current_q = questions[session.current_question_index - 1]
                audio_url = service.get_question_audio_url(current_q, session.language)
                return HttpResponseRedirect(audio_url)
            
            return HttpResponse(status=404)
        except Exception as e:
            logger.error(f"Audio serve error: {e}")
            return HttpResponse(status=404)


class PlivoIVRWebhookView(APIView):
    """
    Plivo-based IVR webhook handling the full call flow:
    Answer URL -> Language selection (DTMF) -> Question Play + Record
    -> Recording STT -> Confirmation (DTMF) -> Completion.
    Returns Plivo Voice XML at every step.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def _is_authorized(self, request):
        configured = settings.PLIVO_WEBHOOK_TOKEN
        supplied = request.headers.get('X-Plivo-Webhook-Token') or request.query_params.get('token', '')
        return bool(configured) and secrets.compare_digest(configured, supplied)

    def _reject_if_unauthorized(self, request):
        if not settings.PLIVO_WEBHOOK_TOKEN:
            logger.critical('Plivo webhook rejected because PLIVO_WEBHOOK_TOKEN is not configured')
            return HttpResponse('service_unavailable', status=503)
        if not self._is_authorized(request):
            logger.warning('Rejected unauthenticated Plivo webhook request')
            return HttpResponse('forbidden', status=403)
        return None

    def _xml(self, body: str) -> HttpResponse:
        return HttpResponse(
            f'<?xml version="1.0" encoding="utf-8"?>\n<Response>\n{body}\n</Response>',
            content_type='application/xml',
        )

    def _action_url(self, request) -> str:
        return request.build_absolute_uri(reverse('plivo-ivr-webhook'))

    def _abs_media(self, request, relative_url: str) -> str:
        if not relative_url:
            return ''
        if relative_url.startswith('http://') or relative_url.startswith('https://'):
            return relative_url
        return request.build_absolute_uri(relative_url)

    # ------------------------------------------------------------------
    # GET  → initial Answer URL (no session yet)
    # POST → subsequent GetInput / Record action callbacks
    # ------------------------------------------------------------------
    def get(self, request):
        return self._handle_webhook(request)

    def post(self, request):
        return self._handle_webhook(request)

    def _handle_webhook(self, request):
        rejection = self._reject_if_unauthorized(request)
        if rejection:
            return rejection

        call_uuid = request.POST.get('CallUUID') or request.GET.get('CallUUID') or ''
        from_number = request.POST.get('From') or request.GET.get('From') or ''
        digits = request.POST.get('Digits') or ''
        record_url = request.POST.get('RecordUrl') or ''

        if not call_uuid:
            logger.error('Plivo webhook missing CallUUID')
            return self._xml('<Speak>System error. Goodbye.</Speak>\n<Hangup/>')

        session, _ = CallSession.objects.get_or_create(
            provider_call_sid=call_uuid,
            defaults={
                'phone_number': from_number or 'unknown',
                'status': CallSession.Status.IN_PROGRESS,
            },
        )

        questions = list(IntakeQuestion.objects.filter(is_active=True).order_by('order'))

        # ----- State machine -----
        if record_url:
            return self._handle_recording(request, session, questions, record_url)

        if session.current_question_index == 0:
            if digits:
                return self._handle_language(request, session, questions, digits)
            return self._ask_language(request)

        if digits:
            return self._handle_confirmation(request, session, questions, digits)

        if session.current_question_index > len(questions):
            return self._complete_call(session)

        return self._ask_question(request, session, questions)

    # ====================== Language Selection ======================

    def _ask_language(self, request):
        action_url = self._action_url(request)
        return self._xml(
            '<GetInput inputType="dtmf" numDigits="1"'
            f' action="{action_url}" method="POST"'
            ' executionTimeout="15000" retries="1">\n'
            '    <Speak>Welcome to JobCare Intake.'
            ' For Hindi press 1. For Kannada press 2.'
            ' For Tamil press 3.</Speak>\n'
            '</GetInput>\n'
            '<Speak>No input received. Goodbye.</Speak>\n'
            '<Hangup/>'
        )

    def _handle_language(self, request, session, questions, digits):
        lang_map = {'1': 'hindi', '2': 'kannada', '3': 'tamil'}
        session.language = lang_map.get(digits, 'hindi')
        session.current_question_index = 1
        session.save()
        if session.current_question_index > len(questions):
            return self._complete_call(session)
        return self._build_question_xml(request, session, questions)

    # ====================== Question Playback ======================

    def _build_question_xml(self, request, session, questions):
        """Build the full XML response for playing a question and recording.
        If request is None the action_url placeholder is left for the caller."""
        current_q = questions[session.current_question_index - 1]
        service = IntakeVoiceService()
        audio_url = service.get_question_audio_url(current_q, session.language)
        if request is not None:
            audio_url = self._abs_media(request, audio_url)
        action_url = self._action_url(request) if request is not None else '{{ACTION_URL}}'

        return self._xml(
            f'<Play>{audio_url}</Play>\n'
            f'<Record action="{action_url}" method="POST"'
            ' maxLength="60" timeout="10"'
            ' finishOnKey="#" playBeep="true" redirect="true" />'
        )

    def _ask_question(self, request, session, questions):
        return self._build_question_xml(request, session, questions)

    # ====================== Recording Callback ======================

    def _handle_recording(self, request, session, questions, record_url):
        current_q = questions[session.current_question_index - 1]

        sarvam = SarvamAIService()
        try:
            resp = requests.get(record_url, timeout=30)
            resp.raise_for_status()
            audio_file = BytesIO(resp.content)
            audio_file.name = 'plivo-recording.wav'
            audio_file.content_type = resp.headers.get('Content-Type', 'audio/wav')
        except Exception as e:
            logger.error(f'Failed to download Plivo recording: {e}')
            return self._retry_recording(request)

        stt_res = sarvam.speech_to_text(audio_file=audio_file, language=normalize_language_code(session.language))
        transcript = stt_res.get('text', '').strip()

        if not transcript:
            return self._retry_recording(request)

        CallAnswer.objects.update_or_create(
            session=session,
            question=current_q,
            defaults={
                'answer_text': transcript,
                'audio_recording_url': record_url,
                'answered_at': timezone.now(),
                'confirmed': False,
            },
        )

        if current_q.question_key in ('name', 'location'):
            return self._ask_confirmation(request, session, current_q)

        session.current_question_index += 1
        session.save()

        if session.current_question_index > len(questions):
            return self._complete_call(session)
        return self._ask_question(request, session, questions)

    def _retry_recording(self, request):
        action_url = self._action_url(request)
        return self._xml(
            '<Speak>Sorry, I could not understand. Please speak clearly after the beep.</Speak>\n'
            f'<Record action="{action_url}" method="POST"'
            ' maxLength="60" timeout="10" finishOnKey="#" playBeep="true"/>'
        )

    # ====================== Confirmation ======================

    def _ask_confirmation(self, request, session, current_q):
        service = IntakeVoiceService()
        last_answer = CallAnswer.objects.filter(
            session=session, question=current_q
        ).order_by('-answered_at').first()
        confirm_url = ''
        if last_answer:
            confirm_url = self._abs_media(
                request,
                service.get_confirmation_audio_url(last_answer.answer_text, session.language),
            )

        action_url = self._action_url(request)
        play_block = f'<Play>{confirm_url}</Play>\n' if confirm_url else ''
        return self._xml(
            f'{play_block}'
            '<GetInput inputType="dtmf" numDigits="1"'
            f' action="{action_url}" method="POST"'
            ' executionTimeout="15000" retries="1">\n'
            '    <Speak>Press 1 to confirm. Press 2 to try again.</Speak>\n'
            '</GetInput>\n'
            '<Speak>No input received. Goodbye.</Speak>\n'
            '<Hangup/>'
        )

    def _handle_confirmation(self, request, session, questions, digits):
        current_q = questions[session.current_question_index - 1]
        answer = CallAnswer.objects.filter(session=session, question=current_q).first()

        if digits == '1':
            if answer:
                answer.confirmed = True
                answer.save()
            session.current_question_index += 1
            session.save()

            if session.current_question_index > len(questions):
                return self._complete_call(session)

            return self._build_question_xml(request, session, questions)
        else:
            return self._build_question_xml(request, session, questions)

    # ====================== Completion ======================

    def _complete_call(self, session):
        if session.status != CallSession.Status.COMPLETED:
            session.status = CallSession.Status.COMPLETED
            session.completed_at = timezone.now()
            session.save()
            process_completed_intake.delay(str(session.id))
        return self._xml(
            '<Speak>Thank you for completing the JobCare intake.'
            ' Your information has been recorded. Goodbye.</Speak>\n'
            '<Hangup/>'
        )


class PlivoHangupView(APIView):
    """
    Plivo Hangup URL — called when a call ends (hangup, timeout, rejection).
    Marks the session as ABANDONED if it's still IN_PROGRESS, preventing
    stale in-progress records from accumulating in the DB.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def _is_authorized(self, request):
        configured = settings.PLIVO_WEBHOOK_TOKEN
        supplied = request.headers.get('X-Plivo-Webhook-Token') or request.query_params.get('token', '')
        return bool(configured) and secrets.compare_digest(configured, supplied)

    def _reject_if_unauthorized(self, request):
        if not settings.PLIVO_WEBHOOK_TOKEN:
            return HttpResponse('service_unavailable', status=503)
        if not self._is_authorized(request):
            return HttpResponse('forbidden', status=403)
        return None

    def post(self, request):
        rejection = self._reject_if_unauthorized(request)
        if rejection:
            return rejection

        call_uuid = request.POST.get('CallUUID') or ''
        event = request.POST.get('Event') or 'hangup'

        if not call_uuid:
            return HttpResponse('ok')

        session = CallSession.objects.filter(provider_call_sid=call_uuid).first()
        if session and session.status == CallSession.Status.IN_PROGRESS:
            session.status = CallSession.Status.ABANDONED
            session.completed_at = timezone.now()
            session.save(update_fields=['status', 'completed_at'])
            logger.info(
                'Plivo hangup: CallSession %s (phone=%s) marked abandoned. '
                'Event=%s, question_index=%s',
                session.id, session.phone_number, event, session.current_question_index,
            )

        return HttpResponse('ok')
