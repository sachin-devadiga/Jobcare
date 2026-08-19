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
    audio = serializers.FileField()
    language = serializers.CharField(default='hi', required=False)

    MAX_AUDIO_SIZE = 20 * 1024 * 1024
    ALLOWED_CONTENT_TYPES = {
        'audio/mpeg', 'audio/mp3', 'audio/mp4', 'audio/x-m4a',
        'audio/wav', 'audio/x-wav', 'audio/webm', 'application/octet-stream',
    }

    def validate_audio(self, value):
        if value.size > self.MAX_AUDIO_SIZE:
            raise serializers.ValidationError('Audio files must be 20 MB or smaller.')
        content_type = getattr(value, 'content_type', '')
        if content_type and content_type.lower() not in self.ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError('Unsupported audio file type.')
        return value


class TextToSpeechSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=5000, trim_whitespace=True)
    language = serializers.CharField(default='hi', required=False)
    voice = serializers.CharField(default='male', required=False)
    pace = serializers.FloatField(default=1.0, min_value=0.5, max_value=2.0, required=False)


class VoiceSearchSerializer(serializers.Serializer):
    query = serializers.CharField()
    language = serializers.CharField(default='hi', required=False)


class ExtractProfileSerializer(serializers.Serializer):
    transcript = serializers.CharField()
    language = serializers.CharField(default='hi', required=False)


class BuildResumeSerializer(serializers.Serializer):
    audio = serializers.FileField()
    language = serializers.CharField(default='hi', required=False)

    MAX_AUDIO_SIZE = 20 * 1024 * 1024
    ALLOWED_CONTENT_TYPES = {
        'audio/mpeg', 'audio/mp3', 'audio/mp4', 'audio/x-m4a',
        'audio/wav', 'audio/x-wav', 'audio/webm', 'application/octet-stream',
    }

    def validate_audio(self, value):
        if value.size > self.MAX_AUDIO_SIZE:
            raise serializers.ValidationError('Audio files must be 20 MB or smaller.')
        content_type = getattr(value, 'content_type', '')
        if content_type and content_type.lower() not in self.ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError('Unsupported audio file type.')
        return value
