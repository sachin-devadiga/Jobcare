from .settings import *  # noqa: F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        '': {'handlers': ['null'], 'level': 'CRITICAL'},
        'django': {'handlers': ['null'], 'level': 'CRITICAL'},
        'django.request': {'handlers': ['null'], 'level': 'CRITICAL'},
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.InMemoryStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# InMemoryStorage still needs a filesystem-shaped base location to resolve
# upload names. It does not write files there.
MEDIA_ROOT = str(BASE_DIR / 'test_media')

RATELIMIT_ENABLE = False

MIDDLEWARE = [m for m in MIDDLEWARE if 'RateLimitMiddleware' not in m]

ALLOWED_HOSTS = ['*']

SECURE_SSL_REDIRECT = False

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
