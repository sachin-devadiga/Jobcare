#!/bin/bash

set -e

echo "=== JobCare Celery Beat Entrypoint ==="

wait_for_service() {
    local host="$1"
    local port="$2"
    local service_name="$3"
    local max_attempts=60
    local attempt=0

    echo "Waiting for $service_name ($host:$port)..."
    while ! nc -z "$host" "$port" 2>/dev/null; do
        attempt=$((attempt + 1))
        if [ "$attempt" -ge "$max_attempts" ]; then
            echo "ERROR: $service_name not available after $max_attempts attempts"
            exit 1
        fi
        sleep 2
    done
    echo "$service_name is available"
}

wait_for_service "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}" "Redis"

echo "=== Clearing Celery Beat database lock (if any) ==="
python manage.py migrate django_celery_beat --noinput 2>/dev/null || true

echo "=== Starting Celery Beat ==="
exec celery -A config beat \
    --loglevel=${CELERY_LOG_LEVEL:-info} \
    --scheduler=django_celery_beat.schedulers:DatabaseScheduler \
    --max-interval=300 \
    --pidfile=/tmp/celery-beat.pid
