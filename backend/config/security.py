import re
import logging
import magic
from urllib.parse import urlparse
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('jobcare')

SQL_INJECTION_PATTERNS = [
    r'\bSELECT\b.*\bFROM\b',
    r'\bDROP\b.*\bTABLE\b',
    r'\bDELETE\b.*\bFROM\b',
    r'\bINSERT\b.*\bINTO\b',
    r'\bUPDATE\b.*\bSET\b',
    r'\bUNION\b.*\bSELECT\b',
    r'\bALTER\b.*\bTABLE\b',
    r'\bCREATE\b.*\bTABLE\b',
    r'\bTRUNCATE\b',
    r'\bEXEC\b.*\bxp_',
    r'\bEXECUTE\b',
    r'\bLOAD_FILE\b',
    r'\bINTO\s+OUTFILE\b',
    r'\bINTO\s+DUMPFILE\b',
    r'--\s',
    r"'.*OR.*'='",
    r"'.*OR\s+1\s*=\s*1",
    r'\bSLEEP\b.*\(',
    r'\bBENCHMARK\b.*\(',
    r'\bWAITFOR\b.*\bDELAY\b',
]

XSS_PATTERNS = [
    r'<script[^>]*>.*?</script>',
    r'javascript\s*:',
    r'on\w+\s*=\s*["\']',
    r'on\w+\s*=\s*[^"\'\s>]+',
    r'<iframe[^>]*>',
    r'<embed[^>]*>',
    r'<object[^>]*>',
    r'<svg[^>]*>.*?<script',
    r'expression\s*\(',
    r'vbscript\s*:',
    r'data\s*:\s*text/html',
    r'<[^>]*\s*style\s*=\s*["\'].*expression.*["\']',
    r'<[^>]*\s*style\s*=\s*["\'].*vbscript.*["\']',
    r'document\.\w+',
    r'window\.\w+',
    r'eval\s*\(',
    r'String\.fromCharCode',
    r'<img[^>]*\s*onerror\s*=',
    r'<body[^>]*\s*onload\s*=',
    r'<input[^>]*\s*onfocus\s*=',
]

ALLOWED_UPLOAD_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.txt', '.csv', '.mp4', '.webm', '.mp3', '.wav', '.ogg',
}

ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain', 'text/csv',
    'video/mp4', 'video/webm', 'video/ogg',
    'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/webm',
}

MAX_UPLOAD_SIZE = 10 * 1024 * 1024

BRUTE_FORCE_THRESHOLD = 5
BRUTE_FORCE_WINDOW = 300
LOCKOUT_DURATION = 900

OTP_MAX_ATTEMPTS = 3
OTP_ATTEMPT_WINDOW = 300


def check_sql_injection(value):
    if not isinstance(value, str):
        return False
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            logger.warning(f'SQL injection attempt detected: pattern={pattern}, value={value[:100]}')
            return True
    return False


def check_xss(value):
    if not isinstance(value, str):
        return False
    for pattern in XSS_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            logger.warning(f'XSS attempt detected: pattern={pattern}, value={value[:100]}')
            return True
    return False


def validate_uploaded_file(uploaded_file):
    errors = []
    ext = ''
    if '.' in uploaded_file.name:
        ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        errors.append(f'File extension "{ext}" is not allowed.')
    if uploaded_file.size > MAX_UPLOAD_SIZE:
        errors.append(f'File size exceeds maximum allowed size of 10MB.')
    try:
        mime_type = magic.from_buffer(uploaded_file.read(2048), mime=True)
        uploaded_file.seek(0)
    except Exception:
        mime_type = ''
        uploaded_file.seek(0)
    if mime_type and mime_type not in ALLOWED_MIME_TYPES:
        errors.append(f'File type "{mime_type}" is not allowed.')
    return errors


def check_brute_force(identifier, action='login'):
    key = f'bf:{action}:{identifier}'
    attempts = cache.get(key, 0)
    if attempts >= BRUTE_FORCE_THRESHOLD:
        lockout_key = f'bf_lockout:{action}:{identifier}'
        lockout_until = cache.get(lockout_key)
        if lockout_until:
            remaining = int(lockout_until - __import__('time').time())
            if remaining > 0:
                return {'locked': True, 'remaining_seconds': remaining, 'attempts': attempts}
            else:
                cache.delete(key)
                cache.delete(lockout_key)
                return {'locked': False, 'attempts': 0}
        cache.set(lockout_key, __import__('time').time() + LOCKOUT_DURATION, LOCKOUT_DURATION)
        return {'locked': True, 'remaining_seconds': LOCKOUT_DURATION, 'attempts': attempts}
    return {'locked': False, 'attempts': attempts}


def record_failed_attempt(identifier, action='login'):
    key = f'bf:{action}:{identifier}'
    attempts = cache.get(key, 0)
    attempts += 1
    cache.set(key, attempts, BRUTE_FORCE_WINDOW)
    return attempts


def reset_brute_force(identifier, action='login'):
    key = f'bf:{action}:{identifier}'
    lockout_key = f'bf_lockout:{action}:{identifier}'
    cache.delete(key)
    cache.delete(lockout_key)


def check_otp_attempts(email):
    key = f'otp_attempts:{email}'
    attempts = cache.get(key, 0)
    if attempts >= OTP_MAX_ATTEMPTS:
        lock_key = f'otp_locked:{email}'
        if cache.get(lock_key):
            return {'allowed': False, 'message': 'Maximum OTP attempts exceeded. Try again later.'}
        cache.set(lock_key, True, OTP_ATTEMPT_WINDOW)
        return {'allowed': False, 'message': 'Maximum OTP attempts exceeded. Try again in 5 minutes.'}
    return {'allowed': True, 'attempts': attempts}


def record_otp_attempt(email):
    key = f'otp_attempts:{email}'
    attempts = cache.get(key, 0)
    attempts += 1
    cache.set(key, attempts, OTP_ATTEMPT_WINDOW)
    return attempts


def reset_otp_attempts(email):
    cache.delete(f'otp_attempts:{email}')
    cache.delete(f'otp_locked:{email}')


class SQLInjectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE'):
            for key, value in request.GET.items():
                if check_sql_injection(value):
                    logger.error(f'SQL injection blocked: {request.path}, param={key}')
                    return JsonResponse(
                        {'success': False, 'message': 'Invalid request parameters'},
                        status=400,
                    )
            if request.method in ('POST', 'PUT', 'PATCH'):
                if hasattr(request, 'data') and isinstance(request.data, dict):
                    for key, value in request.data.items():
                        if isinstance(value, str) and check_sql_injection(value):
                            logger.error(f'SQL injection blocked in body: {request.path}, field={key}')
                            return JsonResponse(
                                {'success': False, 'message': 'Invalid request data'},
                                status=400,
                            )
        return self.get_response(request)


class XSSProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ('POST', 'PUT', 'PATCH'):
            if hasattr(request, 'data') and isinstance(request.data, dict):
                for key, value in request.data.items():
                    if isinstance(value, str) and check_xss(value):
                        logger.warning(f'XSS blocked: {request.path}, field={key}')
                        sanitized = re.sub(r'<[^>]*>', '', value)
                        request.data[key] = sanitized
        return self.get_response(request)


class FileUploadValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ('POST', 'PUT', 'PATCH') and request.FILES:
            for field_name, uploaded_file in request.FILES.items():
                errors = validate_uploaded_file(uploaded_file)
                if errors:
                    logger.warning(f'File upload blocked: {request.path}, file={uploaded_file.name}, errors={errors}')
                    return JsonResponse(
                        {'success': False, 'message': 'File validation failed', 'errors': errors},
                        status=400,
                    )
        return self.get_response(request)


import os
