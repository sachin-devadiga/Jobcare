# Stage 1: Build stage
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        build-essential \
        libpq-dev \
        gettext \
        libffi-dev \
        libssl-dev \
        curl \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

RUN python manage.py collectstatic --noinput --clear 2>/dev/null || true

# Stage 2: Production stage
FROM python:3.12-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings \
    APP_HOME=/app

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        libpq-dev \
        gettext \
        curl \
        libpcre3 \
        libpcre3-dev \
        netcat-openbsd \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p $APP_HOME $APP_HOME/staticfiles $APP_HOME/media $APP_HOME/logs && \
    useradd -m -r -u 1000 -s /bin/false appuser

COPY --from=builder /venv /venv
COPY --from=builder /app $APP_HOME

WORKDIR $APP_HOME

RUN chown -R appuser:appuser $APP_HOME && \
    chmod -R 755 $APP_HOME/staticfiles $APP_HOME/media $APP_HOME/logs

COPY deploy/entrypoint.sh /entrypoint.sh
COPY deploy/entrypoint_celery.sh /entrypoint_celery.sh
COPY deploy/entrypoint_celery_beat.sh /entrypoint_celery_beat.sh
RUN chmod +x /entrypoint.sh /entrypoint_celery.sh /entrypoint_celery_beat.sh

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl --fail http://localhost:8000/api/health/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]
