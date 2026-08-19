import hashlib
import json
import logging
import requests
import time
from urllib.parse import urlparse
from typing import Optional, Dict, Any, List
from django.conf import settings
from django.core.cache import cache
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger('jobcare')


class SarvamAIError(Exception):
    pass


class SarvamAIServiceUnavailableError(SarvamAIError):
    pass


class SarvamAIService:
    SUPPORTED_LANGUAGES = ['hi', 'en', 'ta', 'te', 'kn', 'ml', 'mr', 'gu', 'bn', 'or', 'pa']
    MAX_RETRIES = 3
    STT_TIMEOUT = 60
    TTS_TIMEOUT = 60
    TRANSLATE_TIMEOUT = 30
    CACHE_TTL_STT = 3600
    CACHE_TTL_TTS = 7200

    def __init__(self):
        self.api_key = settings.SARVAM_AI_API_KEY
        self.base_url = settings.SARVAM_AI_BASE_URL
        self._session = self._create_session()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            'api-subscription-key': self.api_key,
            'User-Agent': 'JobCareVoice/1.0',
        })
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=50,
            max_retries=2,
        )
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        return session

    def _normalize_language(self, language: str) -> str:
        lang = language.lower()[:2]
        return lang if lang in self.SUPPORTED_LANGUAGES else 'hi'

    def _language_code(self, language: str) -> str:
        """Return the BCP-47 language code required by current Sarvam APIs."""
        codes = {
            'en': 'en-IN', 'hi': 'hi-IN', 'kn': 'kn-IN',
            'ta': 'ta-IN', 'te': 'te-IN', 'ml': 'ml-IN',
            'mr': 'mr-IN', 'gu': 'gu-IN', 'bn': 'bn-IN',
            'or': 'od-IN', 'pa': 'pa-IN',
        }
        return codes[self._normalize_language(language)]

    def _build_cache_key(self, prefix: str, *args) -> str:
        raw = f'sarvam:{prefix}:{":".join(str(a) for a in args)}'
        if len(raw) > 200 or ' ' in raw:
            return f'sarvam:{prefix}:{hashlib.md5(raw.encode()).hexdigest()}'
        return raw

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
        before_sleep=lambda retry_state: logger.warning(
            f'SarvamAI STT retry {retry_state.attempt_number}/{MAX_RETRIES} after {retry_state.outcome.exception()}'
        ),
    )
    def speech_to_text(
        self,
        audio_url: str = '',
        audio_file=None,
        language: str = 'hi',
        with_diarization: bool = False,
    ) -> Dict[str, Any]:
        lang = self._normalize_language(language)
        if not self.api_key:
            raise SarvamAIServiceUnavailableError('Sarvam AI is not configured')
        source_name = getattr(audio_file, 'name', '') or audio_url
        # Key the cache by audio CONTENT, not the uploaded filename: mobile
        # clients always send the same generic name ('audio.m4a'), so a
        # filename-based key would make every new recording return the first
        # result (often an empty transcript) from cache.
        try:
            if audio_file is not None:
                audio_file.seek(0)
                digest = hashlib.md5(audio_file.read()).hexdigest()
                audio_file.seek(0)
            else:
                digest = audio_url
        except Exception:
            digest = source_name
        cache_key = self._build_cache_key('stt', digest, lang)
        cached = cache.get(cache_key)
        if cached:
            logger.info(f'SarvamAI STT cache hit for {audio_url}')
            return cached

        try:
            url = f'{self.base_url.rstrip("/")}/speech-to-text'
            if audio_file is not None:
                filename = getattr(audio_file, 'name', 'audio.wav')
                content_type = getattr(audio_file, 'content_type', None) or 'application/octet-stream'
                try:
                    audio_file.seek(0)
                except (AttributeError, OSError, ValueError):
                    pass
                files = {'file': (filename, audio_file, content_type)}
            else:
                parsed = urlparse(audio_url)
                allowed_hosts = set(settings.EXOTEL_RECORDING_ALLOWED_HOSTS)
                if parsed.scheme != 'https' or not parsed.hostname or parsed.hostname not in allowed_hosts:
                    raise SarvamAIError('Audio URL is not an approved Exotel recording URL')
                source = requests.get(audio_url, timeout=30)
                source.raise_for_status()
                files = {'file': ('exotel-recording.wav', source.content, source.headers.get('Content-Type', 'audio/wav'))}
            payload = {
                'model': settings.SARVAM_STT_MODEL,
                'language_code': self._language_code(lang),
                'mode': 'transcribe',
            }
            start_time = time.time()
            response = self._session.post(url, data=payload, files=files, timeout=self.STT_TIMEOUT)
            processing_time = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                data = response.json()
                result = {
                    'success': True,
                    'text': data.get('transcript', ''),
                    'language': data.get('language_code', self._language_code(lang)),
                    'confidence': data.get('language_probability'),
                    'processing_time_ms': processing_time,
                    'source': 'api',
                }
                cache.set(cache_key, result, timeout=self.CACHE_TTL_STT)
                logger.info(f'SarvamAI STT success in {processing_time}ms')
                return result
            elif response.status_code == 429:
                logger.warning('SarvamAI STT rate limited, using fallback')
                return self._stt_fallback(lang)
            elif response.status_code >= 500:
                raise SarvamAIServiceUnavailableError(f'SarvamAI server error: {response.status_code}')
            else:
                logger.error(f'SarvamAI STT error: {response.status_code} - {response.text[:200]}')
                return self._stt_fallback(lang)
        except requests.exceptions.Timeout:
            logger.error(f'SarvamAI STT request timed out after {self.STT_TIMEOUT}s')
            return self._stt_fallback(lang)
        except requests.exceptions.ConnectionError as e:
            logger.error(f'SarvamAI STT connection error: {str(e)}')
            return self._stt_fallback(lang)
        except Exception as e:
            logger.error(f'SarvamAI STT error: {str(e)}', exc_info=True)
            return self._stt_fallback(lang)

    def _stt_fallback(self, language: str, legacy_language: Optional[str] = None) -> Dict[str, Any]:
        # Preserve the former (audio_url, language) helper signature without
        # ever using an untrusted URL.
        if legacy_language is not None:
            language = legacy_language
        logger.info('Sarvam STT is unavailable')
        return {
            'success': False,
            'text': '',
            'language': language,
            'confidence': None,
            'processing_time_ms': 0,
            'source': 'fallback',
            'message': 'Voice processing is temporarily unavailable. Please use text search.',
        }

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
        before_sleep=lambda retry_state: logger.warning(
            f'SarvamAI TTS retry {retry_state.attempt_number}/{MAX_RETRIES}'
        ),
    )
    def text_to_speech(
        self,
        text: str,
        language: str = 'hi',
        voice: str = 'male',
        pitch: float = 0.0,
        pace: float = 1.0,
        loudness: float = 1.0,
    ) -> Dict[str, Any]:
        lang = self._normalize_language(language)
        if not self.api_key:
            raise SarvamAIServiceUnavailableError('Sarvam AI is not configured')
        cache_key = self._build_cache_key('tts', text[:50], lang, voice)
        cached = cache.get(cache_key)
        if cached:
            logger.info('SarvamAI TTS cache hit')
            return cached

        try:
            url = f'{self.base_url.rstrip("/")}/text-to-speech'
            payload = {
                'text': text,
                'language_code': self._language_code(lang),
                'model': settings.SARVAM_TTS_MODEL,
                'speaker': 'shubh' if voice in ('', 'default', 'male') else voice,
                'pace': pace,
                'output_audio_codec': 'mp3',
            }
            start_time = time.time()
            response = self._session.post(url, json=payload, timeout=self.TTS_TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                processing_time = int((time.time() - start_time) * 1000)
                result = {
                    'success': True,
                    'audio_url': '',
                    'audio_content': ''.join(data.get('audios', [])),
                    'processing_time_ms': processing_time,
                    'source': 'api',
                }
                cache.set(cache_key, result, timeout=self.CACHE_TTL_TTS)
                logger.info(f'SarvamAI TTS success in {processing_time}ms')
                return result
            elif response.status_code == 429:
                logger.warning('SarvamAI TTS rate limited')
                return self._tts_fallback(text, lang)
            elif response.status_code >= 500:
                raise SarvamAIServiceUnavailableError(f'SarvamAI server error: {response.status_code}')
            else:
                logger.error(f'SarvamAI TTS error: {response.status_code} - {response.text[:200]}')
                return self._tts_fallback(text, lang)
        except requests.exceptions.Timeout:
            logger.error(f'SarvamAI TTS request timed out after {self.TTS_TIMEOUT}s')
            return self._tts_fallback(text, lang)
        except Exception as e:
            logger.error(f'SarvamAI TTS error: {str(e)}', exc_info=True)
            return self._tts_fallback(text, lang)

    def _tts_fallback(self, text: str, language: str) -> Dict[str, Any]:
        logger.info('Using TTS fallback')
        return {
            'success': False,
            'audio_url': None,
            'audio_content': None,
            'processing_time_ms': 0,
            'source': 'fallback',
            'message': 'Voice output is temporarily unavailable.',
        }

    def translate(
        self,
        text: str,
        source_language: str = 'hi',
        target_language: str = 'en',
    ) -> Optional[str]:
        try:
            url = f'{self.base_url.rstrip("/")}/translate'
            payload = {
                'input': text,
                'source_language_code': self._language_code(self._normalize_language(source_language)),
                'target_language_code': self._language_code(self._normalize_language(target_language)),
            }
            response = self._session.post(url, json=payload, timeout=self.TRANSLATE_TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                return data.get('translated_text', '')
            else:
                logger.error(f'SarvamAI translate error: {response.status_code} - {response.text[:200]}')
                return text
        except Exception as e:
            logger.error(f'SarvamAI translate error: {str(e)}')
            return text

    def voice_search(
        self,
        query: str,
        language: str = 'hi',
    ) -> Dict[str, Any]:
        from jobs.repositories.job_repository import JobRepository

        repo = JobRepository()
        try:
            jobs = repo.search(query)
            job_list = [{
                'id': str(j.id),
                'title': j.title,
                'company': j.company.name if hasattr(j, 'company') and j.company else '',
                'city': j.city,
                'salary_min': float(j.salary_min) if j.salary_min else None,
                'salary_max': float(j.salary_max) if j.salary_max else None,
                'job_type': j.job_type,
                'match_reason': self._compute_match_reason(query, j),
            } for j in jobs[:10]]
            return {
                'success': True,
                'query': query,
                'language': language,
                'results_count': len(job_list),
                'total_count': jobs.count() if hasattr(jobs, 'count') else len(job_list),
                'jobs': job_list,
            }
        except Exception as e:
            logger.error(f'Voice search error: {str(e)}', exc_info=True)
            return {
                'success': False,
                'query': query,
                'language': language,
                'results_count': 0,
                'jobs': [],
                'error': 'Search temporarily unavailable',
            }

    def _compute_match_reason(self, query: str, job) -> str:
        query_lower = query.lower()
        reasons = []
        if any(skill.lower() in query_lower for skill in (job.skills_required or [])):
            reasons.append('Skills match')
        if job.city and job.city.lower() in query_lower:
            reasons.append('Location match')
        if job.title and any(word in query_lower for word in job.title.lower().split()):
            reasons.append('Title match')
        return reasons[0] if reasons else 'Relevant opening'

    def process_voice_command(
        self,
        text: str,
        language: str = 'hi',
    ) -> Dict[str, Any]:
        if not text or not text.strip():
            return {
                'success': False,
                'action': 'unknown',
                'message': 'I did not hear anything. Please try again.',
                'query': text,
            }

        text_lower = text.lower().strip()

        intents = {
            'search': ['search', 'find', 'look', 'show', 'jobs', 'naukri', 'position', 'opening', 'vacancy', 'hiring'],
            'navigate_home': ['home', 'go home', 'main page'],
            'navigate_profile': ['profile', 'my profile', 'open profile', 'account'],
            'navigate_applications': ['apply', 'application', 'my application', 'track', 'status'],
            'navigate_messages': ['message', 'chat', 'inbox', 'notification', 'alert'],
            'navigate_saved': ['saved', 'bookmark', 'favourite', 'favorite', 'shortlist'],
            'help': ['help', 'what can you do', 'command', 'how to', 'guide'],
        }

        detected_intent = 'unknown'
        for intent, keywords in intents.items():
            if any(kw in text_lower for kw in keywords):
                detected_intent = intent
                break

        intent_map = {
            'search': self._handle_search_intent,
            'navigate_home': lambda t, l: {'action': 'navigate', 'route': '/home', 'message': 'Going to Home'},
            'navigate_profile': lambda t, l: {'action': 'navigate', 'route': '/profile', 'message': 'Opening your profile'},
            'navigate_applications': lambda t, l: {'action': 'navigate', 'route': '/applications', 'message': 'Showing your applications'},
            'navigate_messages': lambda t, l: {'action': 'navigate', 'route': '/messages', 'message': 'Opening messages'},
            'navigate_saved': lambda t, l: {'action': 'navigate', 'route': '/saved-jobs', 'message': 'Showing saved jobs'},
            'help': lambda t, l: {
                'action': 'help',
                'message': 'I can help you search jobs, apply to positions, check your profile, track applications, and more. Just tell me what you need!',
            },
            'unknown': lambda t, l: {
                'action': 'unknown',
                'message': f'I heard: "{text}". Try saying "Search electrician jobs" or "Open my profile"',
                'query': text,
            },
        }

        handler = intent_map.get(detected_intent, intent_map['unknown'])
        result = handler(text, language)
        result['success'] = True
        result['intent'] = detected_intent
        result['original_query'] = text
        return result

    def _handle_search_intent(self, text: str, language: str) -> Dict[str, Any]:
        query_parts = []
        for word in ['for', 'in', 'near', 'as', 'like', 'with', 'of']:
            if f' {word} ' in f' {text.lower()} ':
                idx = text.lower().index(f' {word} ') + len(word) + 1
                query_parts.append(text[idx:].strip())

        search_query = ' '.join(query_parts) if query_parts else text
        search_result = self.voice_search(search_query, language)

        return {
            'action': 'search',
            'search_query': search_query,
            'message': f'Found {search_result["results_count"]} jobs matching your search',
            'results': search_result,
        }
