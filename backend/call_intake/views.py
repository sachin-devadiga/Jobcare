import logging
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import CallSession, IntakeQuestion, CallAnswer
from .services import IntakeVoiceService
from .tasks import process_completed_intake
from voice_ai.services import SarvamAIService

logger = logging.getLogger('jobcare')

class ExotelIVRWebhookView(APIView):
    """
    The 'Brain' of the IVR. Exotel Passthru applets call this to get the next step.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
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
        stt_res = sarvam.speech_to_text(audio_url=recording_url, language=session.language[:2])
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

class ServeQuestionAudioView(APIView):
    """
    Serves the audio file URL for the Play applet.
    Exotel calls this to know what to play next.
    """
    permission_classes = [AllowAny]

    def get(self, request, session_id):
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
