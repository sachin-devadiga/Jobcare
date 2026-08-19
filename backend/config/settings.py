import os
from datetime import timedelta
from pathlib import Path
from decouple import config, Csv
from django.core.exceptions import ImproperlyConfigured
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = config('DEBUG', default=False, cast=bool)

# A development-only fallback keeps local setup simple while production fails
# closed if its secret has not been injected through the environment.
SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-local-development-key')
if not DEBUG and SECRET_KEY.startswith('django-insecure-'):
    raise ImproperlyConfigured('DJANGO_SECRET_KEY must be set to a secure value when DEBUG is false.')

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

JAZZMIN_SETTINGS = {
    'site_title': 'JobCare Admin',
    'site_header': 'JobCare Voice',
    'site_brand': 'JobCare Voice',
    'site_logo': None,
    'welcome_sign': 'Welcome to JobCare Administration',
    'copyright': 'JobCare Voice Ltd',
    'search_model': ['authentication.User', 'jobs.Job'],
    'topmenu_links': [
        {'name': 'Home', 'url': 'admin:index', 'permissions': ['auth.view_user']},
        {'name': 'API Docs', 'url': '/api/docs/', 'new_window': True},
        {'model': 'authentication.User'},
    ],
    'show_sidebar': True,
    'navigation_expanded': True,
    'order_with_respect_to': [
        'authentication', 'users', 'employers', 'companies', 'jobs',
        'applications', 'chat', 'notifications', 'voice_ai', 'payments',
        'call_intake', 'analytics', 'auth',
    ],
    'icons': {
        'auth': 'fas fa-users-cog',
        'auth.Group': 'fas fa-users',
        'authentication.User': 'fas fa-user',
        'users.EmployeeProfile': 'fas fa-id-card',
        'employers.EmployerProfile': 'fas fa-briefcase',
        'companies.Company': 'fas fa-building',
        'jobs.Job': 'fas fa-file-alt',
        'jobs.Category': 'fas fa-tags',
        'jobs.Skill': 'fas fa-star',
        'applications.Application': 'fas fa-paper-plane',
        'chat.Conversation': 'fas fa-comments',
        'notifications.Notification': 'fas fa-bell',
        'voice_ai.VoiceSession': 'fas fa-microphone',
        'payments.Payment': 'fas fa-credit-card',
        'payments.Subscription': 'fas fa-crown',
        'payments.SubscriptionPlan': 'fas fa-list-alt',
        'call_intake.CallSession': 'fas fa-phone',
        'call_intake.IntakeQuestion': 'fas fa-question-circle',
    },
    'default_icon_parents': 'fas fa-folder',
    'default_icon_children': 'fas fa-circle',
    'related_modal_active': True,
    'custom_css': None,
    'custom_js': None,
    'show_ui_builder': False,
    'changeform_format': 'horizontal_tabs',
    'changeform_format_overrides': {
        'authentication.User': 'vertical_tabs',
        'jobs.Job': 'horizontal_tabs',
    },
    'collapse_action_links': True,
}

JAZZMIN_UI_TWEAKS = {
    'navbar_small_text': False,
    'footer_small_text': False,
    'body_small_text': False,
    'brand_small_text': False,
    'brand_colour': False,
    'accent': 'accent-primary',
    'navbar': 'navbar-dark',
    'no_navbar_border': False,
    'navbar_fixed': True,
    'layout_boxed': False,
    'footer_fixed': False,
    'sidebar_fixed': True,
    'sidebar': 'sidebar-dark-primary',
    'sidebar_nav_small_text': False,
    'sidebar_disable_expand': False,
    'sidebar_nav_child_indent': True,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_flat_style': False,
    'theme': 'default',
    'button_classes': {
        'primary': 'btn-primary',
        'secondary': 'btn-secondary',
        'info': 'btn-info',
        'warning': 'btn-warning',
        'danger': 'btn-danger',
        'success': 'btn-success',
    },
}

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'channels',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'phonenumber_field',
    'django_celery_beat',

    'authentication',
    'users',
    'employers',
    'companies',
    'jobs',
    'applications',
    'chat',
    'notifications',
    'voice_ai',
    'payments',
    'analytics',
    'call_intake',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'config.middleware.SecurityHeadersMiddleware',
    'config.middleware.RequestSizeLimitMiddleware',
    'config.middleware.SQLInjectionDetectionMiddleware',
    'config.middleware.RateLimitMiddleware',
    'config.middleware.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
            'symmetric_encryption_keys': [SECRET_KEY],
        },
    },
}

DATABASES = {
    'default': dj_database_url.config(
        default=f"postgres://{config('DB_USER', default='postgres')}:{config('DB_PASSWORD', default='postgres')}@{config('DB_HOST', default='localhost')}:{config('DB_PORT', default='5432')}/{config('DB_NAME', default='jobcare_db')}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

AUTH_USER_MODEL = 'authentication.User'

AUTHENTICATION_BACKENDS = [
    'authentication.backends.CustomJWTAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'config.exceptions.custom_exception_handler',
    'NON_FIELD_ERRORS_KEY': 'error',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1'],
}

JWT_SIGNING_KEY = config('JWT_SECRET_KEY', default=SECRET_KEY)
if not DEBUG and JWT_SIGNING_KEY == SECRET_KEY:
    raise ImproperlyConfigured('JWT_SECRET_KEY must be configured separately when DEBUG is false.')

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=config('JWT_ACCESS_HOURS', default=24, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_DAYS', default=30, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': JWT_SIGNING_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(hours=24),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=30),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'JobCare Voice API',
    'DESCRIPTION': 'AI-powered voice-enabled job portal API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'Bearer': []}],
    'TAGS': [
        {'name': 'Authentication', 'description': 'User registration, login, OTP verification, password management'},
        {'name': 'Users', 'description': 'Employee profile management'},
        {'name': 'Employers', 'description': 'Employer profile management'},
        {'name': 'Companies', 'description': 'Company management'},
        {'name': 'Jobs', 'description': 'Job listings, search, filtering'},
        {'name': 'Applications', 'description': 'Job applications management'},
        {'name': 'Notifications', 'description': 'Push and email notifications'},
        {'name': 'Voice AI', 'description': 'Voice-based job search and navigation'},
        {'name': 'Payments', 'description': 'Payments and subscriptions'},
        {'name': 'Analytics', 'description': 'Dashboard analytics and reports'},
    ],
}

CELERY_BROKER_URL = config('CELERY_BROKER_URL', default=REDIS_URL)
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=REDIS_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BEAT_SCHEDULE = {
    'cleanup-stale-ivr-sessions': {
        'task': 'call_intake.tasks.cleanup_stale_sessions',
        'schedule': 600.0,
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp-relay.sendinblue.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=10, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@blieve.in')
EMAIL_FROM_NAME = config('EMAIL_FROM_NAME', default='JobCare Voice')
BREVO_API_KEY = config('BREVO_API_KEY', default='')

FIREBASE_CONFIG = {
    'type': config('FIREBASE_TYPE', default=''),
    'project_id': config('FIREBASE_PROJECT_ID', default=''),
    'private_key_id': config('FIREBASE_PRIVATE_KEY_ID', default=''),
    'private_key': config('FIREBASE_PRIVATE_KEY', default='').replace('\\n', '\n'),
    'client_email': config('FIREBASE_CLIENT_EMAIL', default=''),
    'client_id': config('FIREBASE_CLIENT_ID', default=''),
    'auth_uri': config('FIREBASE_AUTH_URI', default='https://accounts.google.com/o/oauth2/auth'),
    'token_uri': config('FIREBASE_TOKEN_URI', default='https://oauth2.googleapis.com/token'),
    'server_key': config('FIREBASE_SERVER_KEY', default=''),
}

RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='')

SARVAM_AI_API_KEY = config('SARVAM_AI_API_KEY', default='')
SARVAM_AI_BASE_URL = config('SARVAM_AI_BASE_URL', default='https://api.sarvam.ai')
SARVAM_STT_MODEL = config('SARVAM_STT_MODEL', default='saaras:v3')
SARVAM_TTS_MODEL = config('SARVAM_TTS_MODEL', default='bulbul:v3')

OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-4o-mini')

# Exotel Configuration
EXOTEL_API_KEY = config('EXOTEL_API_KEY', default='')
EXOTEL_API_TOKEN = config('EXOTEL_API_TOKEN', default='')
EXOTEL_SUBDOMAIN = config('EXOTEL_SUBDOMAIN', default='')
EXOTEL_SID = config('EXOTEL_SID', default='')
EXOTEL_WEBHOOK_TOKEN = config('EXOTEL_WEBHOOK_TOKEN', default='')
EXOTEL_RECORDING_ALLOWED_HOSTS = config('EXOTEL_RECORDING_ALLOWED_HOSTS', default='', cast=Csv())
# Exotel SMS (OTP delivery — same API key/token/SID as Voice/IVR above)
EXOTEL_SMS_SENDER_ID = config('EXOTEL_SMS_SENDER_ID', default='')
EXOTEL_DLT_ENTITY_ID = config('EXOTEL_DLT_ENTITY_ID', default='')
EXOTEL_DLT_TEMPLATE_ID = config('EXOTEL_DLT_TEMPLATE_ID', default='')
EXOTEL_SMS_TYPE = config('EXOTEL_SMS_TYPE', default='transactional')

# Active OTP delivery channel for phone login. 'email' is the temporary
# fallback while Exotel SMS is blocked on DLT approval; flip to 'sms' once
# DLT clears — a one-line config change, no code rewrite.
AUTH_OTP_CHANNEL = config('AUTH_OTP_CHANNEL', default='email')

# Plivo Configuration (replaces Firebase phone auth + powers IVR voice intake)
PLIVO_AUTH_ID = config('PLIVO_AUTH_ID', default='')
PLIVO_AUTH_TOKEN = config('PLIVO_AUTH_TOKEN', default='')
PLIVO_SENDER_NUMBER = config('PLIVO_SENDER_NUMBER', default='')
PLIVO_WEBHOOK_TOKEN = config('PLIVO_WEBHOOK_TOKEN', default='')
PLIVO_RECORDING_ALLOWED_HOSTS = config('PLIVO_RECORDING_ALLOWED_HOSTS', default='s3.amazonaws.com,s3.us-east-1.amazonaws.com,plivo-prod-recording.s3.amazonaws.com', cast=Csv())

LOG_HANDLERS = ['console']
LOG_HANDLERS_ERROR = ['console']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json' if not DEBUG else 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'jobcare': {
            'handlers': ['console'],
            'level': config('APP_LOG_LEVEL', default='DEBUG' if DEBUG else 'INFO'),
            'propagate': False,
        },
    },
}

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
X_FRAME_OPTIONS = 'DENY'

FILE_UPLOAD_ALLOWED_EXTENSIONS = [
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.txt', '.csv', '.mp4', '.webm', '.mp3', '.wav', '.ogg',
]
FILE_UPLOAD_MAX_SIZE_MB = 10

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=not DEBUG, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=False, cast=bool)
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000,http://localhost:5173', cast=Csv())
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']
CORS_ALLOW_HEADERS = [
    'accept', 'authorization', 'content-type', 'origin', 'x-csrftoken',
    'x-requested-with', 'user-agent', 'cache-control',
]
CORS_EXPOSE_HEADERS = ['content-type', 'x-ratelimit-remaining']

RATELIMIT_ENABLE = config('RATELIMIT_ENABLE', default=True, cast=bool)
RATELIMIT_RATE = config('RATELIMIT_RATE', default='200/h', cast=str)
RATELIMIT_AUTH_RATE = config('RATELIMIT_AUTH_RATE', default='10/m', cast=str)

from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'error',
}
