#!/bin/bash

set -e

echo "=== JobCare Celery Worker Entrypoint ==="

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

echo "=== Starting Celery Worker ==="
exec celery -A config worker \
    --loglevel=${CELERY_LOG_LEVEL:-info} \
    --concurrency=${CELERY_CONCURRENCY:-4} \
    --max-tasks-per-child=${CELERY_MAX_TASKS:-1000} \
    --time-limit=${CELERY_TASK_TIME_LIMIT:-1800} \
    --soft-time-limit=${CELERY_SOFT_TIME_LIMIT:-1500} \
    --queues=default,voice,notifications,payments,email \
    --hostname=worker@%h \
    --autoscale=10,2
