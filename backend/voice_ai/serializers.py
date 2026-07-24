from rest_framework import serializers
from .models import VoiceSession


class VoiceSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceSession
        fields = [
            'id', 'user', 'session_type', 'status',
            'audio_input', 'audio_url',
            'input_text', 'output_text', 'output_audio_url',
            'detected_language', 'confidence_score',
            'processing_time_ms', 'metadata', 'error_message',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'status', 'output_text', 'output_audio_url',
                           'detected_language', 'confidence_score', 'processing_time_ms',
                           'error_message', 'created_at', 'updated_at']


class SpeechToTextSerializer(serializers.Serializer):
    audio_url = serializers.URLField(required=False)
    language = serializers.CharField(default='hi', required=False)


class TextToSpeechSerializer(serializers.Serializer):
    text = serializers.CharField()
    language = serializers.CharField(default='hi', required=False)
    voice = serializers.CharField(default='male', required=False)


class VoiceSearchSerializer(serializers.Serializer):
    query = serializers.CharField()
    language = serializers.CharField(default='hi', required=False)


class ExtractProfileSerializer(serializers.Serializer):
    transcript = serializers.CharField()
    language = serializers.CharField(default='hi', required=False)
