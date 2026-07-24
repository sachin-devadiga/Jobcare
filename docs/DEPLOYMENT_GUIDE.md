# JobCare Voice Deployment Guide

## Production Deployment on Hostinger VPS

### Prerequisites

- Hostinger VPS (Ubuntu 22.04 LTS)
- Domain name (e.g., jobcarevoice.com)
- Docker & Docker Compose installed
- Git installed
- SSL Certificate (Let's Encrypt via Certbot)

### Server Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Storage | 40 GB SSD | 80 GB SSD |
| Bandwidth | 2 TB | 4 TB |

---

## Step 1: Initial Server Setup

```bash
# SSH into your VPS
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install essential packages
apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    git \
    ufw \
    fail2ban \
    htop \
    net-tools

# Set up firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

## Step 2: Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version

# Add user to docker group
usermod -aG docker $USER
```

## Step 3: Clone Repository

```bash
# Create application directory
mkdir -p /var/www/jobcare
cd /var/www/jobcare

# Clone repository
git clone https://github.com/your-org/jobcare-voice.git .
```

## Step 4: Configure Environment Variables

```bash
# Create environment file
cp .env.example .env

# Edit environment variables
nano .env
```

### Required Environment Variables

```bash
# Django
DJANGO_SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,api.your-domain.com

# Database
DB_NAME=jobcare_db
DB_USER=jobcare_user
DB_PASSWORD=strong-db-password-here
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key-hear

# Brevo SMTP
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-brevo-email@example.com
EMAIL_HOST_PASSWORD=your-brevo-smtp-key
DEFAULT_FROM_EMAIL=no-reply@jobcarevoice.com

# Razorpay
RAZORPAY_KEY_ID=rzp_live_xxxxxxxx
RAZORPAY_KEY_SECRET=your-razorpay-secret

# Sarvam AI
SARVAM_API_KEY=your-sarvam-api-key
SARVAM_API_URL=https://api.sarvam.ai

# Firebase Cloud Messaging
FCM_CREDENTIALS=/app/credentials/fcm-service-account.json

# Google Maps
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=jobcare-voice-files
AWS_S3_REGION_NAME=ap-south-1

# Sentry (error tracking)
SENTRY_DSN=https://your-sentry-dsn
```

## Step 5: Set Up SSL Certificate

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
certbot certonly --nginx -d your-domain.com -d api.your-domain.com

# Set up auto-renewal
crontab -e
# Add: 0 0 * * * /usr/bin/certbot renew --quiet
```

## Step 6: Firebase Credentials

```bash
# Create credentials directory
mkdir -p /var/www/jobcare/credentials

# Upload your Firebase service account JSON
# Copy the file to /var/www/jobcare/credentials/fcm-service-account.json
```

## Step 7: Build and Deploy

```bash
cd /var/www/jobcare

# Build and start all services
docker-compose -f docker-compose.yml up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

## Step 8: Run Database Migrations

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Load seed data
docker-compose exec backend python manage.py seed_data
```

## Step 9: Verify Deployment

```bash
# Check health endpoint
curl http://localhost:8000/health/

# Check API docs
curl http://localhost:8000/api/docs/

# Check admin panel
curl http://localhost:8000/admin/
```

## Step 10: Set Up Monitoring

```bash
# Install and configure monitoring tools
apt install -y prometheus-node-exporter

# Set up log rotation
cat > /etc/logrotate.d/docker-containers << 'EOF'
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    missingok
    delaycompress
    copytruncate
}
EOF
```

---

## CI/CD with GitHub Actions

The repository includes GitHub Actions workflows for automated deployment:

### Deploy Workflow (`.github/workflows/deploy.yml`)

Triggered on push to `main` branch:

1. Run tests
2. Build Docker images
3. Push images to GitHub Container Registry
4. SSH into VPS
5. Pull latest images
6. Run migrations
7. Restart services
8. Health check

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `DOCKER_USERNAME` | Docker Hub or GHCR username |
| `DOCKER_PASSWORD` | Docker Hub or GHCR token |
| `SSH_HOST` | VPS IP address |
| `SSH_USERNAME` | VPS username (usually root) |
| `SSH_PRIVATE_KEY` | VPS SSH private key |
| `SSH_PORT` | SSH port (usually 22) |
| `SLACK_WEBHOOK_URL` | Slack webhook for failure notifications |

---

## Production Checklist

### Security
- [ ] Firewall configured (UFW)
- [ ] SSH key-only authentication (no passwords)
- [ ] Fail2ban installed and configured
- [ ] SSL certificates installed and auto-renewing
- [ ] Environment variables secured (never in git)
- [ ] Django DEBUG=False
- [ ] Database backed up regularly
- [ ] Rate limiting configured
- [ ] Security headers configured in Nginx

### Performance
- [ ] Redis caching configured
- [ ] Database indexes created
- [ ] Static files served via Nginx/CDN
- [ ] Media files stored on S3
- [ ] Image compression enabled
- [ ] Gzip compression enabled
- [ ] CDN configured for static assets

### Monitoring
- [ ] Sentry error tracking configured
- [ ] Log aggregation set up
- [ ] Health check endpoints active
- [ ] Server resource monitoring active
- [ ] Database query monitoring active
- [ ] Automated backup schedule set

### Backup Strategy

```bash
# Database backup script
#!/bin/bash
BACKUP_DIR="/var/backups/jobcare"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U jobcare_user jobcare_db | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Keep last 30 days of backups
find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /var/www/jobcare/scripts/backup.sh
```

---

## Scaling

### Vertical Scaling
- Increase VPS resources (CPU, RAM)
- Increase database connection limits

### Horizontal Scaling
- Add multiple backend instances behind load balancer
- Use PostgreSQL read replicas
- Distribute Celery workers across multiple servers
- Use CDN for static/media files

### Database Optimization
- Regular VACUUM and ANALYZE
- Query optimization with EXPLAIN ANALYZE
- Connection pooling with PgBouncer
- Table partitioning for large tables

---

## Troubleshooting

### Common Issues

**Issue: 502 Bad Gateway**
```bash
# Check if Gunicorn is running
docker-compose ps backend
# Check backend logs
docker-compose logs backend
```

**Issue: Database Connection Error**
```bash
# Check PostgreSQL status
docker-compose ps postgres
# Check PostgreSQL logs
docker-compose logs postgres
# Verify environment variables
docker-compose exec backend env | grep DB_
```

**Issue: Redis Connection Error**
```bash
# Check Redis status
docker-compose ps redis
# Check Redis logs
docker-compose logs redis
```

**Issue: Celery Tasks Not Running**
```bash
# Check Celery worker status
docker-compose logs celery_worker
# Check Celery beat status
docker-compose logs celery_beat
# Check Redis queue
docker-compose exec redis redis-cli LLEN celery
```

**Issue: Static Files Not Loading**
```bash
# Recollect static files
docker-compose exec backend python manage.py collectstatic --noinput --clear
# Check Nginx static file config
docker-compose exec nginx ls -la /static/
```

### Health Check Commands

```bash
# Backend health
curl http://localhost:8000/health/

# Database connectivity
docker-compose exec backend python -c "from django.db import connection; connection.ensure_connection(); print('OK')"

# Redis connectivity
docker-compose exec backend python -c "import redis; r = redis.Redis.from_url('redis://redis:6379/0'); r.ping(); print('OK')"

# Celery worker status
docker-compose exec backend celery -A config status

# Disk usage
df -h

# Memory usage
free -m

# Docker resource usage
docker stats --no-stream
```

---

## Rollback Procedure

```bash
# Deploy previous version
cd /var/www/jobcare
git revert HEAD
docker-compose down
docker-compose up -d --build

# Or redeploy specific tag
git checkout v1.0.0
docker-compose up -d --build
```

---

## Maintenance Mode

```bash
# Enable maintenance mode
docker-compose exec backend python manage.py maintenance_mode on

# Disable maintenance mode
docker-compose exec backend python manage.py maintenance_mode off
```
