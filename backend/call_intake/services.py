import os
import hashlib
import requests
import base64
import logging
from django.conf import settings
from django.core.files.base import ContentFile
from voice_ai.services import SarvamAIService

logger = logging.getLogger('jobcare')

LANGUAGE_CODE_MAP = {
    'hindi': 'hi',
    'kannada': 'kn',
    'tamil': 'ta',
    'english': 'en',
}


def normalize_language_code(language: str) -> str:
    """Map semantic language names ('kannada') to ISO 639-1 codes ('kn').

    'kannada'[:2] would produce 'ka', which Sarvam does not support
    (it uses 'kn'), so this mapping is required for correct TTS/STT.
    """
    code = LANGUAGE_CODE_MAP.get(str(language).lower(), language)
    return code[:2]

class IntakeVoiceService:
    def __init__(self):
        self.sarvam = SarvamAIService()
        self.cache_dir = os.path.join(settings.MEDIA_ROOT, 'tts_cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_question_audio_url(self, question, language):
        """
        Gets or generates cached TTS for a question.
        Translates English canonical text to target language first.
        """
        text = question.question_text_en
        target_lang_code = normalize_language_code(language)

        if target_lang_code != 'en':
            # Translate canonical English to target language
            text = self.sarvam.translate(
                text, 
                source_language='en', 
                target_language=target_lang_code
            ) or text

        cache_key = hashlib.md5(f"{question.id}_{target_lang_code}".encode()).hexdigest()
        file_name = f"{cache_key}.mp3"
        file_path = os.path.join(self.cache_dir, file_name)

        if not os.path.exists(file_path):
            response = self.sarvam.text_to_speech(
                text=text,
                language=target_lang_code,
            )
            
            if response.get('success'):
                content = None
                if response.get('audio_content'):
                    # Handle base64 content if returned directly
                    try:
                        content = base64.b64decode(response['audio_content'])
                    except:
                        content = response['audio_content'].encode() if isinstance(response['audio_content'], str) else response['audio_content']
                elif response.get('audio_url'):
                    r = requests.get(response['audio_url'])
                    content = r.content

                if content:
                    with open(file_path, 'wb') as f:
                        f.write(content)

        return f"{settings.MEDIA_URL}tts_cache/{file_name}"

    def get_confirmation_audio_url(self, transcript, language):
        """
        Generates and caches dynamic confirmation audio: 'Aapka jawab [X] hai? Sahi ke liye 1 dabayein...'
        Returns the MEDIA_URL path to the cached MP3 file (same pattern as get_question_audio_url).
        """
        target_lang_code = normalize_language_code(language)
        prompts = {
            'hi': f"आपका जवाब {transcript} है? सही के लिए एक दबाएं, दोबारा बोलने के लिए दो।",
            'kn': f"ನಿಮ್ಮ ಉತ್ತರ {transcript}? ಹೌದು ಎಂದಾದರೆ ಒಂದು ಒತ್ತಿ, ಇಲ್ಲವಾದರೆ ಎರಡು ಒತ್ತಿ.",
            'ta': f"உங்கள் பதில் {transcript}? சரி என்றால் ஒன்றை அழுத்தவும், தவறு என்றால் இரண்டை அழுத்தவும்.",
            'en': f"Your answer is {transcript}. Press 1 for yes, 2 to retry."
        }
        full_text = prompts.get(target_lang_code, prompts['en'])

        cache_key = hashlib.md5(f"confirm_{transcript}_{target_lang_code}".encode()).hexdigest()
        file_name = f"{cache_key}.mp3"
        file_path = os.path.join(self.cache_dir, file_name)

        if not os.path.exists(file_path):
            response = self.sarvam.text_to_speech(text=full_text, language=target_lang_code)
            if response.get('success'):
                content = None
                if response.get('audio_content'):
                    try:
                        content = base64.b64decode(response['audio_content'])
                    except Exception:
                        content = response['audio_content'].encode() if isinstance(response['audio_content'], str) else response['audio_content']
                elif response.get('audio_url'):
                    r = requests.get(response['audio_url'])
                    content = r.content
                if content:
                    with open(file_path, 'wb') as f:
                        f.write(content)

        return f"{settings.MEDIA_URL}tts_cache/{file_name}"
