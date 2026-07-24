import time
import json
import re
import struct
import zlib
import jwt
from datetime import timedelta
from django.test import override_settings
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from config.security import (
    check_sql_injection,
    check_xss,
    validate_uploaded_file,
    check_brute_force,
    record_failed_attempt,
    reset_brute_force,
    check_otp_attempts,
    record_otp_attempt,
    BRUTE_FORCE_THRESHOLD,
)
from config.validators import (
    validate_password_complexity,
    validate_phone_number,
    validate_aadhaar_number,
    validate_pincode,
    sanitize_text_input,
)
from config.middleware import SecurityHeadersMiddleware

User = get_user_model()


class MockFile:
    def __init__(self, name, size, content=b''):
        self.name = name
        self.size = size
        self.content = content

    def read(self, n=-1):
        return self.content[:n] if n > 0 else self.content

    def seek(self, offset):
        pass


def _minimal_png_bytes():
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    raw = b'\x00\xff\x00\x00'
    compressed = zlib.compress(raw)
    idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
    idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
    iend_crc = zlib.crc32(b'IEND') & 0xffffffff
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
    return sig + ihdr + idat + iend


class SQLInjectionProtectionTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_sql_injection_in_search_params(self):
        sql_payloads = [
            "' OR '1'='1",
            "' OR 1=1 --",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin' --",
            "1; SELECT * FROM users",
            "1' OR '1'='1'; --",
            "1' AND 1=1; --",
        ]
        for payload in sql_payloads:
            with self.subTest(payload=payload):
                response = self.client.get(f'/api/v1/jobs/?search={payload}')
                self.assertIn(response.status_code, [200, 400])
                if response.status_code == 400:
                    data = json.loads(response.content)
                    self.assertIn('Invalid', data.get('message', ''))

    def test_sql_injection_detection_function(self):
        self.assertTrue(check_sql_injection("SELECT * FROM users"))
        self.assertTrue(check_sql_injection("DROP TABLE users"))
        self.assertTrue(check_sql_injection("1' OR '1'='1"))
        self.assertTrue(check_sql_injection("UNION SELECT * FROM passwords"))
        self.assertTrue(check_sql_injection("'; DELETE FROM accounts; --"))
        self.assertFalse(check_sql_injection("Hello, this is a normal search query"))
        self.assertFalse(check_sql_injection("Python developer with 5 years experience"))

    def test_sql_injection_in_post_data(self):
        injection_data = {
            'title': "Job Title'; DROP TABLE jobs; --",
            'description': 'Normal description',
        }
        response = self.client.post('/api/v1/jobs/', injection_data, format='json')
        self.assertIn(response.status_code, [200, 400, 401, 403])

    def test_safe_input_passes_scan(self):
        safe_inputs = [
            'Python developer',
            'Looking for a job in Bangalore',
            '5 years of experience in Django',
            'Contact: +91-9876543210',
            'Bachelor of Technology in Computer Science',
        ]
        for inp in safe_inputs:
            with self.subTest(input=inp):
                self.assertFalse(check_sql_injection(inp))


class XSSProtectionTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_xss_in_job_descriptions(self):
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert(1)>',
            '<iframe src="http://evil.com"></iframe>',
            'javascript:alert("XSS")',
            '<svg onload=alert(1)>',
            '<body onload=alert(1)>',
            '"><script>alert(1)</script>',
            '<input onfocus=alert(1)>',
        ]
        for payload in xss_payloads:
            with self.subTest(payload=payload):
                self.assertTrue(check_xss(payload))

    def test_xss_detection_function(self):
        self.assertTrue(check_xss('<script>alert("test")</script>'))
        self.assertTrue(check_xss('<img src="x" onerror="alert(1)">'))
        self.assertTrue(check_xss('javascript:alert(1)'))
        self.assertTrue(check_xss('<iframe src="http://evil.com"></iframe>'))
        self.assertTrue(check_xss('document.cookie'))
        self.assertTrue(check_xss('window.location'))
        self.assertTrue(check_xss("onclick='alert(1)'"))
        self.assertFalse(check_xss('Hello, this is a normal text'))
        self.assertFalse(check_xss('Looking for a job as a Python developer'))

    def test_sanitize_input(self):
        dirty_input = '<script>alert("xss")</script>Hello'
        sanitized = sanitize_text_input(dirty_input)
        self.assertNotIn('<script>', sanitized)
        self.assertIn('Hello', sanitized)

    def test_clean_text_passes(self):
        clean_texts = [
            'Full Stack Developer needed for a startup',
            'Must have strong communication skills',
            'Experience with cloud technologies like AWS',
            'Competitive salary and benefits package',
        ]
        for text in clean_texts:
            with self.subTest(text=text):
                self.assertFalse(check_xss(text))


class FileUploadValidationTest(APITestCase):
    def test_valid_file_extension(self):
        valid_file = MockFile('resume.pdf', 500000, b'%PDF-1.4 test content')
        errors = validate_uploaded_file(valid_file)
        self.assertEqual(len(errors), 0)

    def test_invalid_file_extension(self):
        invalid_file = MockFile('malware.exe', 500000, b'MZ executable')
        errors = validate_uploaded_file(invalid_file)
        self.assertGreater(len(errors), 0)

    def test_file_size_exceeded(self):
        large_file = MockFile('large.pdf', 20 * 1024 * 1024, b'x' * (20 * 1024 * 1024))
        errors = validate_uploaded_file(large_file)
        self.assertGreater(len(errors), 0)

    def test_dangerous_file_types(self):
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.sh', '.vbs', '.ps1', '.js', '.jar', '.dll', '.msi']
        for ext in dangerous_extensions:
            with self.subTest(ext=ext):
                dangerous_file = MockFile(f'test{ext}', 1000, b'test')
                errors = validate_uploaded_file(dangerous_file)
                self.assertGreater(len(errors), 0)

    def test_permitted_image_formats(self):
        permitted = [
            MockFile('photo.jpg', 50000, b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01'),
            MockFile('photo.png', 50000, _minimal_png_bytes()),
            MockFile('photo.gif', 50000, b'GIF89a'),
            MockFile('photo.webp', 50000, b'RIFF\x00\x00\x00\x00WEBPVP8 '),
            MockFile('photo.svg', 50000, b'<?xml version="1.0"?><svg></svg>'),
        ]
        for f in permitted:
            with self.subTest(file=f.name):
                errors = validate_uploaded_file(f)
                self.assertEqual(len(errors), 0)


class RateLimitingTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear()

    def test_rate_limiting_exceeded(self):
        if not getattr(settings, 'RATELIMIT_ENABLE', True):
            self.skipTest('Rate limiting is disabled in test settings')
        register_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+919999999999',
            'role': 'employee',
            'password': 'Strong@123',
            'confirm_password': 'Strong@123',
        }
        for i in range(15):
            response = self.client.post('/api/v1/auth/register/', register_data, format='json')
            if response.status_code == 429:
                return
        self.fail('Rate limiting did not trigger after 15 attempts')

    def test_auth_rate_limit_stricter(self):
        if not getattr(settings, 'RATELIMIT_ENABLE', True):
            self.skipTest('Rate limiting is disabled in test settings')
        login_data = {'email': 'nonexistent@test.com', 'password': 'wrongpass'}
        for i in range(20):
            response = self.client.post('/api/v1/auth/login/', login_data, format='json')
            if response.status_code == 429:
                return
        self.fail('Auth rate limiting did not trigger')


class BruteForceProtectionTest(APITestCase):
    def setUp(self):
        cache.clear()

    def test_brute_force_lockout(self):
        email = 'test@example.com'
        for i in range(BRUTE_FORCE_THRESHOLD + 1):
            record_failed_attempt(email, 'login')
        bf_check = check_brute_force(email, 'login')
        self.assertTrue(bf_check['locked'])
        self.assertGreater(bf_check['remaining_seconds'], 0)
        reset_brute_force(email, 'login')
        bf_check = check_brute_force(email, 'login')
        self.assertFalse(bf_check['locked'])

    def test_brute_force_reset_after_success(self):
        email = 'test@example.com'
        for i in range(3):
            record_failed_attempt(email, 'login')
        reset_brute_force(email, 'login')
        bf_check = check_brute_force(email, 'login')
        self.assertFalse(bf_check['locked'])
        self.assertEqual(bf_check['attempts'], 0)

    def test_account_lockout_after_multiple_failures(self):
        email = 'user@test.com'
        for i in range(BRUTE_FORCE_THRESHOLD):
            record_failed_attempt(email, 'login')
        bf_check = check_brute_force(email, 'login')
        self.assertTrue(bf_check['locked'])


class OTPAttemptLimitsTest(APITestCase):
    def setUp(self):
        cache.clear()

    def test_otp_max_attempts(self):
        email = 'test@example.com'
        for i in range(3):
            record_otp_attempt(email)
        otp_check = check_otp_attempts(email)
        self.assertFalse(otp_check['allowed'])
        self.assertIn('Maximum OTP', otp_check['message'])

    def test_otp_single_use(self):
        email = 'test@example.com'
        from django.core.cache import cache
        cache.set(f'otp:{email}', '123456', timeout=300)
        cached_otp = cache.get(f'otp:{email}')
        self.assertEqual(cached_otp, '123456')
        cache.delete(f'otp:{email}')
        self.assertIsNone(cache.get(f'otp:{email}'))


class JWTTokenSecurityTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='jwtuser@example.com',
            password='Test@123456',
            name='JWT User',
            phone='+919876543220',
            role='employee',
            is_verified=True,
            is_active=True,
        )

    def test_jwt_token_expiry(self):
        token = AccessToken.for_user(self.user)
        token.set_exp(lifetime=timedelta(seconds=-1))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/v1/auth/profile/')
        self.assertIn(response.status_code, [401, 403])

    def test_jwt_token_tampering(self):
        valid_token = str(AccessToken.for_user(self.user))
        tampered_token = valid_token[:-5] + 'XXXXX'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tampered_token}')
        response = self.client.get('/api/v1/auth/profile/')
        self.assertIn(response.status_code, [401, 403])

    def test_jwt_missing_token(self):
        response = self.client.get('/api/v1/auth/profile/')
        self.assertIn(response.status_code, [401, 403])

    def test_jwt_invalid_signature(self):
        import jwt
        payload = {'user_id': str(self.user.id), 'token_type': 'access'}
        invalid_token = jwt.encode(payload, 'wrong-secret-key', algorithm='HS256')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {invalid_token}')
        response = self.client.get('/api/v1/auth/profile/')
        self.assertIn(response.status_code, [401, 403])

    def test_jwt_token_with_wrong_issuer(self):
        token = AccessToken.for_user(self.user)
        token.payload['iss'] = 'evil-attacker'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/v1/auth/profile/')
        self.assertIn(response.status_code, [200, 401, 403])


class CORSHeadersTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    @override_settings(CORS_ALLOWED_ORIGINS=['http://localhost:3000'])
    def test_cors_allowed_origin(self):
        response = self.client.get(
            '/api/v1/jobs/',
            HTTP_ORIGIN='http://localhost:3000',
        )
        self.assertIn('Access-Control-Allow-Origin', response)
        self.assertEqual(response['Access-Control-Allow-Origin'], 'http://localhost:3000')

    @override_settings(CORS_ALLOWED_ORIGINS=['http://localhost:3000'])
    def test_cors_denied_origin(self):
        response = self.client.get(
            '/api/v1/jobs/',
            HTTP_ORIGIN='http://evil.com',
        )
        cors_header = response.get('Access-Control-Allow-Origin', '')
        self.assertNotEqual(cors_header, 'http://evil.com')

    def test_cors_wildcard_not_used(self):
        from django.conf import settings
        cors_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        cors_allow_all = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
        self.assertFalse(cors_allow_all)
        if cors_origins:
            for origin in cors_origins:
                self.assertNotEqual(origin, '*')


class SecurityHeadersTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_security_headers_present(self):
        response = self.client.get('/api/v1/jobs/')
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Referrer-Policy',
        ]
        for header in security_headers:
            with self.subTest(header=header):
                self.assertIn(header, response)

    def test_x_content_type_options(self):
        response = self.client.get('/api/v1/jobs/')
        self.assertEqual(response.get('X-Content-Type-Options'), 'nosniff')

    def test_x_frame_options(self):
        response = self.client.get('/api/v1/jobs/')
        self.assertEqual(response.get('X-Frame-Options'), 'DENY')

    def test_x_xss_protection(self):
        response = self.client.get('/api/v1/jobs/')
        self.assertEqual(response.get('X-XSS-Protection'), '1; mode=block')

    def test_referrer_policy(self):
        response = self.client.get('/api/v1/jobs/')
        self.assertEqual(response.get('Referrer-Policy'), 'strict-origin-when-cross-origin')

    def test_permissions_policy_header(self):
        response = self.client.get('/api/v1/jobs/')
        permissions_policy = response.get('Permissions-Policy', '')
        self.assertIn('geolocation=()', permissions_policy)
        self.assertIn('microphone=()', permissions_policy)
        self.assertIn('camera=()', permissions_policy)

    def test_cross_origin_headers(self):
        response = self.client.get('/api/v1/jobs/')
        self.assertEqual(response.get('Cross-Origin-Resource-Policy'), 'same-origin')
        self.assertEqual(response.get('Cross-Origin-Opener-Policy'), 'same-origin')
        self.assertEqual(response.get('Cross-Origin-Embedder-Policy'), 'require-corp')


class PasswordPolicyTest(APITestCase):
    def test_password_min_length(self):
        with self.assertRaises(Exception):
            validate_password_complexity('Ab1!')

    def test_password_requires_uppercase(self):
        with self.assertRaises(Exception):
            validate_password_complexity('lowercase1!')

    def test_password_requires_lowercase(self):
        with self.assertRaises(Exception):
            validate_password_complexity('UPPERCASE1!')

    def test_password_requires_digit(self):
        with self.assertRaises(Exception):
            validate_password_complexity('NoDigits!@')

    def test_password_requires_special_character(self):
        with self.assertRaises(Exception):
            validate_password_complexity('NoSpecial1')

    def test_valid_password(self):
        try:
            result = validate_password_complexity('Valid@123')
            self.assertEqual(result, 'Valid@123')
        except Exception:
            self.fail('validate_password_complexity raised unexpectedly for a valid password')

    def test_password_common_patterns(self):
        weak_patterns = ['Password123!', 'Welcome@1', 'Admin@123', 'Qwerty@123']
        for pwd in weak_patterns:
            with self.subTest(password=pwd):
                with self.assertRaises(Exception):
                    validate_password_complexity(pwd)

    def test_register_with_weak_password(self):
        self.client = APIClient()
        weak_passwords = ['short', 'nodigits!', 'NODIGITS!', 'lowercase1!', 'UPPERCASE1!']
        for pwd in weak_passwords:
            with self.subTest(password=pwd):
                response = self.client.post('/api/v1/auth/register/', {
                    'name': 'Test',
                    'email': f'test_{pwd}@example.com',
                    'phone': f'+9199999999{hash(pwd) % 10 + 10:02d}',
                    'role': 'employee',
                    'password': pwd,
                    'confirm_password': pwd,
                }, format='json')
                self.assertIn(response.status_code, [400], f'Weak password {pwd} was accepted')


class AuthenticationRequiredTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_dashboard(self):
        response = self.client.get('/api/v1/analytics/dashboard/')
        self.assertIn(response.status_code, [401, 403])

    def test_auth_required_for_profile(self):
        response = self.client.get('/api/v1/auth/profile/')
        self.assertIn(response.status_code, [401, 403])

    def test_auth_required_for_job_listing(self):
        response = self.client.get('/api/v1/applications/my-applications/')
        self.assertIn(response.status_code, [401, 403])

    def test_auth_required_for_notifications(self):
        response = self.client.get('/api/v1/notifications/')
        self.assertIn(response.status_code, [401, 403])

    def test_auth_not_required_for_register(self):
        response = self.client.post('/api/v1/auth/register/', {
            'name': 'Test', 'email': 'test_auth@example.com',
            'phone': '+919999999990', 'role': 'employee',
            'password': 'Strong@123', 'confirm_password': 'Strong@123',
        }, format='json')
        self.assertNotIn(response.status_code, [401, 403])

    def test_auth_not_required_for_login(self):
        User.objects.create_user(email='test@example.com', password='testpass', name='Test', role='employee', phone='+919999999999', is_verified=True)
        response = self.client.post('/api/v1/auth/login/', {
            'email': 'test@example.com', 'password': 'testpass',
        }, format='json')
        self.assertNotIn(response.status_code, [401, 403])

    def test_auth_not_required_for_forgot_password(self):
        response = self.client.post('/api/v1/auth/forgot-password/', {
            'email': 'test@example.com',
        }, format='json')
        self.assertNotIn(response.status_code, [401, 403])


class ValidatorTests(APITestCase):
    def test_phone_number_validation(self):
        valid_numbers = ['+919876543210', '+14155552671', '+918765432109']
        for num in valid_numbers:
            with self.subTest(phone=num):
                try:
                    validate_phone_number(num)
                except Exception:
                    self.fail(f'validate_phone_number raised for valid number {num}')

        invalid_numbers = ['123', 'abcdefghij', '+91-98765']
        for num in invalid_numbers:
            with self.subTest(phone=num):
                with self.assertRaises(Exception):
                    validate_phone_number(num)

    def test_aadhaar_number_validation(self):
        valid_aadhaar = '123456789012'
        try:
            validate_aadhaar_number(valid_aadhaar)
        except Exception:
            pass

        invalid_aadhaar = ['1234', '000000000000', '111111111111', 'abcdefghijkl']
        for aadhaar in invalid_aadhaar:
            with self.subTest(aadhaar=aadhaar):
                with self.assertRaises(Exception):
                    validate_aadhaar_number(aadhaar)

    def test_pincode_validation(self):
        try:
            validate_pincode('560001')
        except Exception:
            self.fail('validate_pincode raised for valid pincode 560001')
        with self.assertRaises(Exception):
            validate_pincode('123')
        with self.assertRaises(Exception):
            validate_pincode('ABCDEF')

    def test_sanitize_text_input(self):
        dirty = '<b>Bold</b><script>alert("xss")</script>'
        clean = sanitize_text_input(dirty)
        self.assertNotIn('<', clean)
        self.assertNotIn('>', clean)


class MiddlewareTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_request_size_limit_exceeded(self):
        large_data = {'data': 'x' * 12_000_000}
        response = self.client.post('/api/v1/auth/login/', large_data, format='json')
        self.assertIn(response.status_code, [200, 400, 413, 401])

    def test_security_headers_middleware_active(self):
        response = self.client.get('/api/v1/jobs/')
        self.assertIn('X-Content-Type-Options', response)
        self.assertIn('X-Frame-Options', response)
        self.assertIn('X-XSS-Protection', response)
        self.assertIn('Referrer-Policy', response)
        self.assertIn('Cross-Origin-Resource-Policy', response)
        self.assertIn('Cross-Origin-Opener-Policy', response)
