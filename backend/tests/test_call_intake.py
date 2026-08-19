from unittest.mock import patch

import pytest
from rest_framework import status


WEBHOOK_URL = '/api/v1/intake/webhook/exotel/'


@pytest.fixture
def webhook_settings(settings):
    settings.EXOTEL_WEBHOOK_TOKEN = 'test-webhook-secret'


class TestExotelWebhookAuthentication:
    def test_rejects_missing_webhook_token(self, api_client, webhook_settings):
        response = api_client.post(WEBHOOK_URL, {'CallSid': 'call-1'}, format='multipart')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_rejects_invalid_webhook_token(self, api_client, webhook_settings):
        response = api_client.post(
            WEBHOOK_URL, {'CallSid': 'call-1'}, format='multipart', HTTP_X_EXOTEL_WEBHOOK_TOKEN='wrong',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch('call_intake.views.IntakeVoiceService.get_question_audio_url', return_value='https://audio.example/question.mp3')
    def test_accepts_header_token(self, mock_audio, api_client, webhook_settings):
        response = api_client.post(
            WEBHOOK_URL, {'CallSid': 'call-1', 'From': '+919876543210'}, format='multipart',
            HTTP_X_EXOTEL_WEBHOOK_TOKEN='test-webhook-secret',
        )
        assert response.status_code == status.HTTP_200_OK


def test_exotel_webhook_fails_closed_when_secret_is_unconfigured(api_client, settings):
    settings.EXOTEL_WEBHOOK_TOKEN = ''
    response = api_client.post(WEBHOOK_URL, {'CallSid': 'call-1'}, format='multipart')
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
