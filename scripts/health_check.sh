#!/bin/bash
set -euo pipefail

API_URL="${API_URL:-https://api.jobcarevoice.com}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-jobcare_db}"
DB_USER="${DB_USER:-postgres}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"
SSL_DOMAIN="${SSL_DOMAIN:-api.jobcarevoice.com}"
LOG_FILE="/var/log/healthcheck.log"
ALERT_LOG="/var/log/healthcheck_alerts.log"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

failures=0
max_failures=0

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

alert() {
    local message="$1"
    local level="${2:-ERROR}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [${level}] ${message}" >> "$ALERT_LOG"
    if [ -n "$SLACK_WEBHOOK" ]; then
        local color="danger"
        [ "$level" = "WARNING" ] && color="warning"
        curl -s -X POST "$SLACK_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"attachments\": [{\"color\": \"${color}\", \"title\": \"Health Check: ${level}\", \"text\": \"${message}\", \"footer\": \"JobCare Voice Monitor\", \"ts\": $(date +%s)}]}" \
            > /dev/null 2>&1 || true
    fi
}

check_api() {
    log "Checking API health endpoint..."
    local status_code
    status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "${API_URL}/health/" 2>/dev/null || echo "000")
    if [ "$status_code" = "200" ]; then
        echo -e "  ${GREEN}API Health: OK (200)${NC}"
        return 0
    else
        echo -e "  ${RED}API Health: FAILED (${status_code})${NC}"
        alert "API health check FAILED with status ${status_code} on ${API_URL}"
        failures=$((failures + 1))
        return 1
    fi
}

check_api_response_time() {
    log "Checking API response time..."
    local start end duration
    start=$(date +%s%N)
    curl -s -o /dev/null --max-time 10 "${API_URL}/health/" > /dev/null 2>&1 || true
    end=$(date +%s%N)
    duration=$(( (end - start) / 1000000 ))
    if [ "$duration" -lt 500 ]; then
        echo -e "  ${GREEN}API Response Time: ${duration}ms (OK)${NC}"
    elif [ "$duration" -lt 2000 ]; then
        echo -e "  ${YELLOW}API Response Time: ${duration}ms (SLOW)${NC}"
    else
        echo -e "  ${RED}API Response Time: ${duration}ms (CRITICAL)${NC}"
        alert "API response time critical: ${duration}ms" "WARNING"
    fi
}

check_database() {
    log "Checking database connectivity..."
    if command -v psql &> /dev/null; then
        if PGPASSWORD="${DB_PASSWORD:-postgres}" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            -c "SELECT 1;" > /dev/null 2>&1; then
            echo -e "  ${GREEN}Database: Connected${NC}"

            local conn_count
            conn_count=$(PGPASSWORD="${DB_PASSWORD:-postgres}" psql \
                -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
                -t -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';" 2>/dev/null | tr -d ' ')
            echo -e "  Active connections: ${conn_count}"
            return 0
        else
            echo -e "  ${RED}Database: Connection FAILED${NC}"
            alert "Database connection FAILED to ${DB_HOST}:${DB_PORT}/${DB_NAME}"
            failures=$((failures + 1))
            return 1
        fi
    else
        echo -e "  ${YELLOW}Database: psql not installed, skipping${NC}"
        return 0
    fi
}

check_redis() {
    log "Checking Redis connectivity..."
    if command -v redis-cli &> /dev/null; then
        if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping 2>/dev/null | grep -q "PONG"; then
            echo -e "  ${GREEN}Redis: Connected${NC}"
            local mem_usage
            mem_usage=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" INFO memory 2>/dev/null | grep "used_memory_human" | cut -d: -f2)
            echo -e "  Memory usage: ${mem_usage}"
            return 0
        else
            echo -e "  ${RED}Redis: Connection FAILED${NC}"
            alert "Redis connection FAILED to ${REDIS_HOST}:${REDIS_PORT}"
            failures=$((failures + 1))
            return 1
        fi
    else
        echo -e "  ${YELLOW}Redis: redis-cli not installed, skipping${NC}"
        return 0
    fi
}

check_celery() {
    log "Checking Celery worker status..."
    local celery_available=false
    if command -v celery &> /dev/null; then
        if celery -A config inspect ping -j 2>/dev/null | grep -q "pong"; then
            celery_available=true
        fi
    fi
    if curl -s --max-time 5 "${API_URL}/health/celery/" > /dev/null 2>&1; then
        celery_available=true
    fi
    if [ "$celery_available" = true ]; then
        echo -e "  ${GREEN}Celery Workers: Running${NC}"
    else
        echo -e "  ${YELLOW}Celery Workers: Status unknown (no direct check)${NC}"
    fi
}

check_disk_space() {
    log "Checking disk space..."
    local usage
    usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$usage" -lt 80 ]; then
        echo -e "  ${GREEN}Disk Usage: ${usage}%${NC}"
    elif [ "$usage" -lt 90 ]; then
        echo -e "  ${YELLOW}Disk Usage: ${usage}% (WARNING)${NC}"
    else
        echo -e "  ${RED}Disk Usage: ${usage}% (CRITICAL)${NC}"
        alert "Disk space critical: ${usage}% used on /"
        failures=$((failures + 1))
    fi
}

check_memory() {
    log "Checking memory usage..."
    if command -v free &> /dev/null; then
        local total used percent
        total=$(free -m | awk '/^Mem:/ {print $2}')
        used=$(free -m | awk '/^Mem:/ {print $3}')
        percent=$((used * 100 / total))
        if [ "$percent" -lt 80 ]; then
            echo -e "  ${GREEN}Memory: ${used}MB/${total}MB (${percent}%)${NC}"
        elif [ "$percent" -lt 90 ]; then
            echo -e "  ${YELLOW}Memory: ${used}MB/${total}MB (${percent}%) (WARNING)${NC}"
        else
            echo -e "  ${RED}Memory: ${used}MB/${total}MB (${percent}%) (CRITICAL)${NC}"
            alert "Memory usage critical: ${percent}%"
        fi
    else
        echo -e "  ${YELLOW}Memory: free not available${NC}"
    fi
}

check_ssl_certificate() {
    log "Checking SSL certificate expiry..."
    local expiry_date days_left
    expiry_date=$(openssl s_client -servername "$SSL_DOMAIN" -connect "${SSL_DOMAIN}:443" </dev/null 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    if [ -n "$expiry_date" ]; then
        days_left=$(( ($(date -d "$expiry_date" +%s) - $(date +%s)) / 86400 ))
        if [ "$days_left" -gt 30 ]; then
            echo -e "  ${GREEN}SSL Certificate: Expires in ${days_left} days${NC}"
        elif [ "$days_left" -gt 7 ]; then
            echo -e "  ${YELLOW}SSL Certificate: Expires in ${days_left} days (RENEW SOON)${NC}"
            alert "SSL certificate expires in ${days_left} days for ${SSL_DOMAIN}" "WARNING"
        else
            echo -e "  ${RED}SSL Certificate: Expires in ${days_left} days (CRITICAL)${NC}"
            alert "SSL certificate expires in ${days_left} days for ${SSL_DOMAIN}"
            failures=$((failures + 1))
        fi
    else
        echo -e "  ${YELLOW}SSL Certificate: Could not check${NC}"
    fi
}

check_nginx() {
    log "Checking Nginx status..."
    if command -v nginx &> /dev/null; then
        if nginx -t 2>/dev/null; then
            echo -e "  ${GREEN}Nginx: Configuration OK${NC}"
        else
            echo -e "  ${RED}Nginx: Configuration ERROR${NC}"
            alert "Nginx configuration test FAILED"
            failures=$((failures + 1))
        fi
    else
        echo -e "  ${YELLOW}Nginx: Not installed locally, skipping${NC}"
    fi
}

main() {
    echo ""
    echo "=========================================="
    echo "  JobCare Voice - Health Check"
    echo "  $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
    echo ""
    log "Starting health check..."

    check_api
    check_api_response_time
    check_database
    check_redis
    check_celery
    check_disk_space
    check_memory
    check_ssl_certificate
    check_nginx

    echo ""
    echo "=========================================="
    if [ $failures -eq 0 ]; then
        echo -e "  ${GREEN}All checks passed${NC}"
        exit 0
    else
        echo -e "  ${RED}${failures} checks FAILED${NC}"
        exit 1
    fi
    echo "=========================================="
    echo ""
}

main "$@"
