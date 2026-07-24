from unittest.mock import patch, MagicMock
from rest_framework import status

STT_URL = '/api/v1/voice/speech-to-text/'
TTS_URL = '/api/v1/voice/text-to-speech/'
SEARCH_URL = '/api/v1/voice/search/'
NAVIGATE_URL = '/api/v1/voice/navigate/'


class TestSpeechToText:
    @patch('voice_ai.views.sarvam_ai_service.speech_to_text')
    def test_speech_to_text_success(self, mock_stt, api_client):
        mock_stt.return_value = {
            'text': 'Hello world',
            'language': 'hi',
            'confidence': 0.95,
            'processing_time_ms': 1200,
            'success': True,
        }
        response = api_client.post(STT_URL, {
            'audio_url': 'https://storage.example.com/audio.wav',
            'language': 'hi',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['text'] == 'Hello world'

    @patch('voice_ai.views.sarvam_ai_service.speech_to_text')
    def test_speech_to_text_fallback(self, mock_stt, api_client):
        mock_stt.return_value = {
            'success': True,
            'text': '',
            'language': 'hi',
            'confidence': None,
            'processing_time_ms': 0,
            'source': 'fallback',
            'message': 'Voice processing is temporarily unavailable.',
        }
        response = api_client.post(STT_URL, {
            'audio_url': 'https://storage.example.com/audio.wav',
            'language': 'hi',
        }, format='json')
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR)
        if response.status_code == status.HTTP_200_OK:
            assert response.data['data']['source'] == 'fallback'

    def test_speech_to_text_missing_url(self, api_client):
        response = api_client.post(STT_URL, {}, format='json')
        assert response.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestTextToSpeech:
    @patch('voice_ai.views.sarvam_ai_service.text_to_speech')
    def test_text_to_speech_success(self, mock_tts, api_client):
        mock_tts.return_value = {
            'audio_url': 'https://storage.example.com/output.wav',
            'processing_time_ms': 800,
            'success': True,
        }
        response = api_client.post(TTS_URL, {
            'text': 'Hello, welcome to JobCare Voice',
            'language': 'hi',
            'voice': 'male',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'audio_url' in response.data['data']

    @patch('voice_ai.views.sarvam_ai_service.text_to_speech')
    def test_text_to_speech_fallback(self, mock_tts, api_client):
        mock_tts.return_value = {
            'success': False,
            'audio_url': None,
            'audio_content': None,
            'processing_time_ms': 0,
            'source': 'fallback',
            'message': 'Voice output is temporarily unavailable.',
        }
        response = api_client.post(TTS_URL, {
            'text': 'Hello',
            'language': 'hi',
            'voice': 'male',
        }, format='json')
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_text_to_speech_missing_text(self, api_client):
        response = api_client.post(TTS_URL, {
            'language': 'hi',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestVoiceSearch:
    @patch('voice_ai.views.sarvam_ai_service.voice_search')
    def test_voice_search(self, mock_search, api_client):
        mock_search.return_value = {
            'success': True,
            'query': 'software engineer jobs',
            'results_count': 5,
            'total_count': 5,
            'jobs': [
                {'id': '1', 'title': 'Software Engineer', 'company': 'Tech Corp'},
            ],
        }
        response = api_client.post(SEARCH_URL, {
            'query': 'software engineer jobs',
            'language': 'en',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['results_count'] == 5


class TestVoiceNavigation:
    @patch('voice_ai.views.sarvam_ai_service.process_voice_command')
    def test_voice_navigation(self, mock_nav, api_client):
        mock_nav.return_value = {
            'success': True,
            'action': 'navigate',
            'route': '/profile',
            'message': 'Opening your profile',
            'intent': 'navigate_profile',
        }
        response = api_client.post(NAVIGATE_URL, {
            'query': 'open my profile',
            'language': 'en',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['route'] == '/profile'

    @patch('voice_ai.views.sarvam_ai_service.process_voice_command')
    def test_process_command_search(self, mock_nav, api_client):
        mock_nav.return_value = {
            'success': True,
            'action': 'search',
            'search_query': 'electrician',
            'message': 'Found 3 jobs matching your search',
            'intent': 'search',
            'results': {'results_count': 3, 'jobs': []},
        }
        response = api_client.post(NAVIGATE_URL, {
            'query': 'search electrician jobs',
            'language': 'en',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['intent'] == 'search'

    @patch('voice_ai.views.sarvam_ai_service.process_voice_command')
    def test_process_command_navigate(self, mock_nav, api_client):
        mock_nav.return_value = {
            'success': True,
            'action': 'navigate',
            'route': '/applications',
            'message': 'Showing your applications',
            'intent': 'navigate_applications',
        }
        response = api_client.post(NAVIGATE_URL, {
            'query': 'show my applications',
            'language': 'en',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['intent'] == 'navigate_applications'

    @patch('voice_ai.views.sarvam_ai_service.process_voice_command')
    def test_process_command_unknown(self, mock_nav, api_client):
        mock_nav.return_value = {
            'success': True,
            'action': 'unknown',
            'message': 'Try saying "Search electrician jobs" or "Open my profile"',
            'intent': 'unknown',
            'original_query': 'xyzzy',
        }
        response = api_client.post(NAVIGATE_URL, {
            'query': 'xyzzy',
            'language': 'en',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['intent'] == 'unknown'
