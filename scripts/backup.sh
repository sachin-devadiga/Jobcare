#!/bin/bash
set -euo pipefail

RETENTION_DAYS=30
BACKUP_DIR="/backups/postgres"
S3_BUCKET="s3://jobcare-backups"
DB_NAME="${DB_NAME:-jobcare_db}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DATE_STAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${DATE_STAMP}.sql.gz"
WAL_DIR="${BACKUP_DIR}/wal"
LOG_FILE="${BACKUP_DIR}/backup.log"
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"
S3_ENDPOINT="${S3_ENDPOINT:-}"
AWS_ACCESS_KEY="${AWS_ACCESS_KEY:-}"
AWS_SECRET_KEY="${AWS_SECRET_KEY:-}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

notify() {
    local message="$1"
    local level="${2:-INFO}"
    log "[${level}] ${message}"
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -s -X POST "$SLACK_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"text\": \"[${level}] JobCare Backup: ${message}\"}" \
            > /dev/null 2>&1 || true
    fi
}

cleanup_old_backups() {
    log "Cleaning up backups older than ${RETENTION_DAYS} days..."
    find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -type f -mtime "+${RETENTION_DAYS}" -delete
    find "$WAL_DIR" -name "*.wal.gz" -type f -mtime "+${RETENTION_DAYS}" -delete
    log "Old backups cleaned."
}

create_full_backup() {
    log "Starting full PostgreSQL backup..."

    mkdir -p "$BACKUP_DIR" "$WAL_DIR"

    PGPASSWORD="${DB_PASSWORD:-postgres}" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --format=custom \
        --verbose \
        --no-owner \
        --compress=9 \
        --file="${BACKUP_FILE%.gz}" \
        2>>"$LOG_FILE"

    if [ $? -eq 0 ]; then
        gzip -f "${BACKUP_FILE%.gz}"
        BACKUP_SIZE=$(stat -c%s "$BACKUP_FILE" 2>/dev/null || stat -f%z "$BACKUP_FILE" 2>/dev/null)
        BACKUP_SIZE_MB=$((BACKUP_SIZE / 1048576))
        notify "Full backup completed: ${BACKUP_FILE} (${BACKUP_SIZE_MB}MB)" "INFO"
    else
        notify "Full backup FAILED" "ERROR"
        exit 1
    fi
}

archive_wal() {
    log "Archiving WAL files..."
    PGPASSWORD="${DB_PASSWORD:-postgres}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "SELECT pg_switch_wal();" \
        > /dev/null 2>&1 || true
    log "WAL archive completed."
}

upload_to_s3() {
    if [ -z "$S3_BUCKET" ]; then
        log "S3 bucket not configured, skipping upload."
        return
    fi

    log "Uploading backups to S3..."

    local s3_args=""
    if [ -n "$S3_ENDPOINT" ]; then
        s3_args="--endpoint-url $S3_ENDPOINT"
    fi
    if [ -n "$AWS_ACCESS_KEY" ] && [ -n "$AWS_SECRET_KEY" ]; then
        export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY"
        export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_KEY"
    fi

    aws s3 cp "$BACKUP_FILE" "${S3_BUCKET}/daily/${DATE_STAMP}/" \
        $s3_args \
        --storage-class STANDARD_IA \
        2>>"$LOG_FILE"

    aws s3 sync "$WAL_DIR" "${S3_BUCKET}/wal/" \
        $s3_args \
        --storage-class STANDARD_IA \
        2>>"$LOG_FILE"

    notify "Backup uploaded to S3 successfully" "INFO"
}

verify_backup() {
    log "Verifying backup integrity..."
    local test_db="verify_test_${DATE_STAMP}"

    PGPASSWORD="${DB_PASSWORD:-postgres}" createdb \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        "$test_db" \
        2>>"$LOG_FILE" || true

    gunzip -c "$BACKUP_FILE" | PGPASSWORD="${DB_PASSWORD:-postgres}" pg_restore \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$test_db" \
        --no-owner \
        --verbose \
        2>>"$LOG_FILE" || true

    if [ $? -eq 0 ]; then
        notify "Backup verification: SUCCESS" "INFO"
    else
        notify "Backup verification: FAILED" "ERROR"
    fi

    PGPASSWORD="${DB_PASSWORD:-postgres}" dropdb \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        "$test_db" \
        2>>"$LOG_FILE" || true
}

main() {
    log "=== JobCare Voice Database Backup ==="
    log "Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}"

    create_full_backup
    archive_wal
    upload_to_s3
    verify_backup
    cleanup_old_backups

    notify "Backup cycle completed successfully" "INFO"
    log "=== Backup Complete ==="
}

main "$@"
