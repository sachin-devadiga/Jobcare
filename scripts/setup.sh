#!/bin/bash

set -e

echo "=========================================="
echo "  JobCare Voice - Project Setup Script"
echo "=========================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Check prerequisites
check_command() {
    if ! command -v "$1" &>/dev/null; then
        echo "ERROR: $1 is not installed. Please install it first."
        exit 1
    fi
}

echo ""
echo "Checking prerequisites..."
check_command docker
check_command docker compose

echo "  [OK] Docker installed"
echo "  [OK] Docker Compose installed"

# Create .env file if not exists
if [ ! -f "$PROJECT_ROOT/backend/.env" ]; then
    echo ""
    echo "Creating backend/.env from .env.example..."
    cp "$PROJECT_ROOT/backend/.env.example" "$PROJECT_ROOT/backend/.env"
    echo "  [OK] .env file created"
    echo ""
    echo "=========================================="
    echo "  IMPORTANT: Edit backend/.env with your"
    echo "  actual configuration values before"
    echo "  running in production!"
    echo "=========================================="
fi

# Create required directories
echo ""
echo "Creating required directories..."
mkdir -p "$PROJECT_ROOT/backend/static"
mkdir -p "$PROJECT_ROOT/backend/media"
mkdir -p "$PROJECT_ROOT/backend/logs"
mkdir -p "$PROJECT_ROOT/backend/credentials"
mkdir -p "$PROJECT_ROOT/deploy/postgres"
echo "  [OK] Directories created"

# Create postgres init script
if [ ! -f "$PROJECT_ROOT/deploy/postgres/init.sql" ]; then
    echo ""
    echo "Creating PostgreSQL initialization script..."
    cat > "$PROJECT_ROOT/deploy/postgres/init.sql" << 'SQL_EOF'
-- PostgreSQL initialization script
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";
SQL_EOF
    echo "  [OK] init.sql created"
fi

# Build Docker images
echo ""
echo "Building Docker images..."
docker compose build --pull
echo "  [OK] Docker images built"

# Start services
echo ""
echo "Starting services..."
docker compose up -d postgres redis
echo "Waiting for databases to be ready..."
sleep 10

# Run migrations
echo ""
echo "Running database migrations..."
docker compose run --rm backend python manage.py migrate --noinput
echo "  [OK] Migrations applied"

# Collect static files
echo ""
echo "Collecting static files..."
docker compose run --rm backend python manage.py collectstatic --noinput --clear 2>/dev/null || true
echo "  [OK] Static files collected"

# Create superuser
echo ""
echo "Creating superuser..."
docker compose run --rm backend python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='admin@jobcare.voice',
        phone='9999999999',
        password='admin123',
        user_type='admin',
        is_active=True,
        is_staff=True
    )
    print('Superuser created: admin@jobcare.voice / admin123')
else:
    print('Superuser already exists')
"

# Load seed data
echo ""
echo "Loading seed data..."
docker compose run --rm backend python manage.py seed_data
echo "  [OK] Seed data loaded"

# Start all services
echo ""
echo "Starting all services..."
docker compose up -d
echo "  [OK] All services started"

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "  Backend API:  http://localhost:8000/api/"
echo "  Admin Panel:  http://localhost:8000/admin/"
echo "  API Docs:     http://localhost:8000/api/docs/"
echo "  PostgreSQL:   localhost:5432"
echo "  Redis:        localhost:6379"
echo ""
echo "  Default Admin Credentials:"
echo "    Email:    admin@jobcare.voice"
echo "    Phone:    9999999999"
echo "    Password: admin123"
echo ""
echo "=========================================="
echo "  To stop services: docker compose down"
echo "  To view logs:     docker compose logs -f"
echo "=========================================="
