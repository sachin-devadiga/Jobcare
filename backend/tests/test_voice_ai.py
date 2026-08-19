import base64
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status


STT_URL = '/api/v1/voice/speech-to-text/'
TTS_URL = '/api/v1/voice/text-to-speech/'
SEARCH_URL = '/api/v1/voice/search/'
NAVIGATE_URL = '/api/v1/voice/navigate/'


def audio_upload(name='recording.m4a', content=b'audio bytes', content_type='audio/mp4'):
    return SimpleUploadedFile(name, content, content_type=content_type)


class TestVoiceAuthentication:
    def test_voice_endpoints_require_authentication(self, api_client):
        for url, data in (
            (STT_URL, {'audio': audio_upload()}),
            (TTS_URL, {'text': 'Hello'}),
            (SEARCH_URL, {'query': 'electrician jobs'}),
            (NAVIGATE_URL, {'query': 'open profile'}),
        ):
            response = api_client.post(url, data, format='multipart' if url == STT_URL else 'json')
            assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSpeechToText:
    @patch('voice_ai.views.sarvam_ai_service.speech_to_text')
    def test_authenticated_multipart_upload(self, mock_stt, auth_client):
        mock_stt.return_value = {
            'text': 'Hello world', 'language': 'hi-IN', 'confidence': 0.95,
            'processing_time_ms': 1200, 'success': True,
        }
        response = auth_client.post(
            STT_URL, {'audio': audio_upload(), 'language': 'hi'}, format='multipart',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['text'] == 'Hello world'
        assert mock_stt.call_args.kwargs['audio_file'].name == 'recording.m4a'

    def test_rejects_missing_or_invalid_audio(self, auth_client):
        response = auth_client.post(STT_URL, {'language': 'hi'}, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response = auth_client.post(
            STT_URL, {'audio': audio_upload('audio.txt', b'x', 'text/plain')}, format='multipart',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'audio' in response.data['errors']

    @patch('voice_ai.views.sarvam_ai_service.speech_to_text')
    def test_provider_failure_is_not_reported_as_transcription(self, mock_stt, auth_client):
        mock_stt.return_value = {'success': False, 'text': ''}
        response = auth_client.post(STT_URL, {'audio': audio_upload()}, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestTextToSpeech:
    @patch('voice_ai.views.sarvam_ai_service.text_to_speech')
    def test_base64_audio_is_stored_and_returned_as_url(self, mock_tts, auth_client):
        mock_tts.return_value = {
            'success': True,
            'audio_content': base64.b64encode(b'fake mp3 bytes').decode(),
            'processing_time_ms': 800,
        }
        response = auth_client.post(TTS_URL, {'text': 'Hello, welcome to JobCare Voice'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['audio_url'].endswith('.mp3')

    @patch('voice_ai.views.sarvam_ai_service.text_to_speech')
    def test_invalid_provider_base64_is_rejected(self, mock_tts, auth_client):
        mock_tts.return_value = {'success': True, 'audio_content': 'not base64!', 'processing_time_ms': 1}
        response = auth_client.post(TTS_URL, {'text': 'Hello'}, format='json')
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_tts_validates_text(self, auth_client):
        response = auth_client.post(TTS_URL, {'text': ''}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestVoiceCommands:
    @patch('voice_ai.views.sarvam_ai_service.voice_search')
    def test_voice_search(self, mock_search, auth_client):
        mock_search.return_value = {'query': 'software engineer jobs', 'results_count': 1, 'jobs': []}
        response = auth_client.post(SEARCH_URL, {'query': 'software engineer jobs', 'language': 'en'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['results_count'] == 1

    @patch('voice_ai.views.sarvam_ai_service.process_voice_command')
    def test_voice_navigation(self, mock_nav, auth_client):
        mock_nav.return_value = {'action': 'navigate', 'route': '/profile', 'message': 'Opening profile'}
        response = auth_client.post(NAVIGATE_URL, {'query': 'open my profile'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['route'] == '/profile'
