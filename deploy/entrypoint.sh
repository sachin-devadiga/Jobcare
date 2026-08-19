#!/bin/bash

set -e

echo "=== JobCare Voice Backend Entrypoint ==="

echo "=== Running database migrations ==="
python manage.py migrate --noinput

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --clear 2>/dev/null || echo "Static file collection skipped"

echo "=== Creating cache tables ==="
python manage.py createcachetable --noinput 2>/dev/null || true

echo "=== Creating superuser (if not exists) ==="
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='${DJANGO_SUPERUSER_EMAIL:-admin@jobcare.voice}',
        phone='${DJANGO_SUPERUSER_PHONE:-9999999999}',
        password='${DJANGO_SUPERUSER_PASSWORD:-ChangeMeInProduction!}',
        role='admin',
        name='Admin',
        is_active=True,
        is_staff=True
    )
    print('Superuser created')
else:
    print('Superuser already exists')
"

echo "=== Starting Gunicorn ==="
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-4} \
    --worker-class sync \
    --timeout 120 \
    --graceful-timeout 60 \
    --keep-alive 5 \
    --max-requests 2000 \
    --max-requests-jitter 500 \
    --log-level ${GUNICORN_LOG_LEVEL:-info} \
    --access-logfile - \
    --error-logfile - \
    --access-logformat '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
