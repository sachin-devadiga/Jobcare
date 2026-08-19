"""Gunicorn configuration for JobCare backend."""

import multiprocessing
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Server socket
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")
backlog = int(os.environ.get("GUNICORN_BACKLOG", 2048))

# Worker processes
workers = int(os.environ.get(
    "GUNICORN_WORKERS",
    multiprocessing.cpu_count() * 2 + 1,
))
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "sync")
threads = int(os.environ.get("GUNICORN_THREADS", 1))
worker_connections = int(os.environ.get("GUNICORN_WORKER_CONNECTIONS", 1000))
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", 2000))
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", 500))
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 120))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", 60))
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", 5))

# Process naming
proc_name = "jobcare"
pythonpath = BASE_DIR

# Logging
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
accesslog = os.environ.get("GUNICORN_ACCESS_LOG", "-")
errorlog = os.environ.get("GUNICORN_ERROR_LOG", "-")
access_log_format = os.environ.get(
    "GUNICORN_ACCESS_LOG_FORMAT",
    '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"',
)

# SSL (disabled by default, handled by nginx)
keyfile = os.environ.get("GUNICORN_KEYFILE", None)
certfile = os.environ.get("GUNICORN_CERTFILE", None)

# Security & limits
limit_request_line = int(os.environ.get("GUNICORN_LIMIT_REQUEST_LINE", 4094))
limit_request_fields = int(os.environ.get("GUNICORN_LIMIT_REQUEST_FIELDS", 100))
limit_request_field_size = int(os.environ.get("GUNICORN_LIMIT_REQUEST_FIELD_SIZE", 8190))

# Server mechanics
daemon = False
pidfile = None
umask = 0o022
user = os.environ.get("GUNICORN_USER", None)
group = os.environ.get("GUNICORN_GROUP", None)
tmp_upload_dir = os.environ.get("GUNICORN_TMP_UPLOAD_DIR", None)

# Spew (debug)
spew = False

# Preload app for faster worker startup
preload_app = True

# Check config
check_config = False

# Reload (development)
reload = os.environ.get("DEBUG", "0") == "1"
reload_extra_files = []


def when_ready(server):
    """Log when server is ready."""
    server.log.info(
        "JobCare server ready on %s with %d workers",
        bind,
        workers,
    )


def on_starting(server):
    """Log on starting."""
    server.log.info("Starting JobCare Gunicorn server")


def on_exit(server):
    """Log on exit."""
    server.log.info("Stopping JobCare Gunicorn server")


def worker_int(worker):
    """Log worker interrupt."""
    worker.log.info("Worker received INT signal")


def worker_abort(worker):
    """Log worker abort."""
    worker.log.info("Worker received ABORT signal")


def post_fork(server, worker):
    """Log after forking a worker."""
    server.log.debug("Worker spawned (pid: %s)", worker.pid)


def pre_exec(server):
    """Log before exec."""
    server.log.info("Forked child, re-executing")


def pre_request(worker, req):
    """Log before each request."""
    worker.log.debug("Processing request: %s %s", req.method, req.path)


def post_request(worker, req, environ, resp):
    """Log after each request."""
    worker.log.debug(
        "Finished request: %s %s - %s",
        req.method,
        req.path,
        resp.status,
    )
