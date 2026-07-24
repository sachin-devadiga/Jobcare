import time
import logging
import json
import re
from typing import Optional
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.http.request import RawPostDataException
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('jobcare')

RATE_LIMIT_BYPASS_PATHS = [
    r'^/admin/',
    r'^/static/',
    r'^/media/',
    r'^/health/',
    r'^/api/docs/',
]

AUTH_PATHS = [
    r'^/api/v1/auth/login',
    r'^/api/v1/auth/register',
    r'^/api/v1/auth/verify-otp',
    r'^/api/v1/auth/forgot-password',
    r'^/api/v1/auth/reset-password',
]


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        path = request.path_info

        if self._should_bypass(path):
            return self.get_response(request)

        if self._is_auth_path(path):
            if self._is_rate_limited(request, 'auth', limit=10, window=60):
                return JsonResponse(
                    {'success': False, 'message': 'Too many requests. Please try again later.', 'retry_after': 60},
                    status=429,
                )
        else:
            identifier = str(request.user.id) if request.user.is_authenticated else request.META.get('REMOTE_ADDR', 'unknown')
            if request.user.is_authenticated:
                if self._is_rate_limited(request, 'api', limit=200, window=60):
                    return JsonResponse(
                        {'success': False, 'message': 'Rate limit exceeded. Please slow down.', 'retry_after': 60},
                        status=429,
                    )
            else:
                if self._is_rate_limited(request, 'anon', limit=30, window=60):
                    return JsonResponse(
                        {'success': False, 'message': 'Rate limit exceeded for anonymous users.', 'retry_after': 60},
                        status=429,
                    )

        return self.get_response(request)

    def _should_bypass(self, path: str) -> bool:
        return any(re.match(pattern, path) for pattern in RATE_LIMIT_BYPASS_PATHS)

    def _is_auth_path(self, path: str) -> bool:
        return any(re.match(pattern, path) for pattern in AUTH_PATHS)

    def _is_rate_limited(self, request: HttpRequest, prefix: str, limit: int, window: int) -> bool:
        identifier = str(request.user.id) if request.user.is_authenticated else request.META.get('REMOTE_ADDR', 'unknown')
        cache_key = f'ratelimit:{prefix}:{identifier}'
        hits = cache.get(cache_key, 0)
        if hits >= limit:
            return True
        cache.set(cache_key, hits + 1, timeout=window)
        return False


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        request.start_time = time.time()
        response = self.get_response(request)
        self._log_request(request, response)
        return response

    def _log_request(self, request: HttpRequest, response):
        duration = time.time() - request.start_time
        user = str(request.user) if request.user.is_authenticated else 'anonymous'
        status_code = response.status_code

        log_data = {
            'method': request.method,
            'path': request.get_full_path(),
            'status': status_code,
            'duration_ms': round(duration * 1000, 2),
            'user': user,
            'ip': request.META.get('REMOTE_ADDR', ''),
            'ua': request.META.get('HTTP_USER_AGENT', '')[:100],
        }

        if status_code >= 500:
            logger.error(json.dumps(log_data))
        elif status_code >= 400:
            logger.warning(json.dumps(log_data))
        elif duration > 2.0:
            log_data['slow'] = True
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=(), payment=()'
        response['Cross-Origin-Resource-Policy'] = 'same-origin'
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com",
                "img-src 'self' data: blob: https:",
                "font-src 'self' https://fonts.gstatic.com",
                "connect-src 'self' https: wss:",
                "frame-src 'none'",
                "object-src 'none'",
                "base-uri 'self'",
                "form-action 'self'",
            ]
            response['Content-Security-Policy'] = '; '.join(csp_directives)
        return response


class RequestSizeLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        content_length = request.META.get('CONTENT_LENGTH')
        if content_length:
            try:
                if int(content_length) > settings.DATA_UPLOAD_MAX_MEMORY_SIZE:
                    return JsonResponse(
                        {'success': False, 'message': 'Request body too large'},
                        status=413,
                    )
            except (ValueError, TypeError):
                pass
        return self.get_response(request)


class SQLInjectionDetectionMiddleware:
    SQL_PATTERNS = [
        r"(\bSELECT\b.*\bFROM\b|UNION.*SELECT|INSERT.*INTO|DELETE.*FROM|UPDATE.*SET|DROP\s+TABLE|ALTER\s+TABLE|CREATE\s+TABLE|TRUNCATE|EXEC\s*\(|EXECUTE\s*\(|LOAD_FILE\s*\(|INTO\s+OUTFILE|INTO\s+DUMPFILE|--\s|'.*OR\s+1\s*=\s*1|SLEEP\s*\(|BENCHMARK\s*\()",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        for key, value in request.GET.items():
            if isinstance(value, str):
                for pattern in self.SQL_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        logger.warning(f'SQL injection attempt blocked: {request.path}, param={key}')
                        return JsonResponse(
                            {'success': False, 'message': 'Invalid request parameters'},
                            status=400,
                        )
        for key, value in request.POST.items():
            if isinstance(value, str):
                for pattern in self.SQL_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        logger.warning(f'SQL injection attempt blocked: {request.path}, field={key}')
                        return JsonResponse(
                            {'success': False, 'message': 'Invalid request data'},
                            status=400,
                        )
        if request.method in ('POST', 'PUT', 'PATCH'):
            try:
                body_str = request.body.decode('utf-8', errors='ignore')
                for pattern in self.SQL_PATTERNS:
                    if re.search(pattern, body_str, re.IGNORECASE):
                        logger.warning(f'SQL injection attempt blocked in body: {request.path}')
                        return JsonResponse(
                            {'success': False, 'message': 'Invalid request data'},
                            status=400,
                        )
            except (Exception, RawPostDataException):
                pass
        return self.get_response(request)
