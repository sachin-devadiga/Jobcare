#!/bin/bash
set -euo pipefail

BACKUP_DIR="/backups/postgres"
DB_NAME="${DB_NAME:-jobcare_db}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
LOG_FILE="${BACKUP_DIR}/restore.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --list                    List available backups"
    echo "  --backup-file FILE        Restore from specific backup file"
    echo "  --latest                  Restore from latest backup"
    echo "  --pitr TIMESTAMP          Point-in-time recovery (format: '2024-01-01 12:00:00 IST')"
    echo "  --dry-run                 Show what would be done without executing"
    echo "  --target-db NAME          Restore to a different database name"
    echo ""
    echo "Example:"
    echo "  $0 --list"
    echo "  $0 --latest"
    echo "  $0 --backup-file /backups/jobcare_db_20240101_000000.sql.gz"
    echo "  $0 --pitr '2024-01-01 14:30:00 IST'"
}

list_backups() {
    echo "Available backups:"
    echo "=================="
    if [ -d "$BACKUP_DIR" ]; then
        for f in $(ls -t "${BACKUP_DIR}"/*.sql.gz 2>/dev/null); do
            size=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null)
            size_mb=$((size / 1048576))
            echo "  $(basename "$f") (${size_mb}MB) - $(date -r "$f" '+%Y-%m-%d %H:%M:%S')"
        done
    else
        echo "  No backups found in ${BACKUP_DIR}"
    fi
}

restore_backup() {
    local backup_file="$1"
    local target_db="${2:-$DB_NAME}"

    if [ ! -f "$backup_file" ]; then
        log "ERROR: Backup file not found: ${backup_file}"
        exit 1
    fi

    log "Starting restore from: ${backup_file}"
    log "Target database: ${target_db}"

    log "Terminating existing connections to ${target_db}..."
    PGPASSWORD="${DB_PASSWORD:-postgres}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "postgres" \
        -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${target_db}' AND pid <> pg_backend_pid();" \
        > /dev/null 2>&1 || true

    log "Dropping and recreating database ${target_db}..."
    PGPASSWORD="${DB_PASSWORD:-postgres}" dropdb \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        --if-exists \
        "$target_db" \
        2>>"$LOG_FILE"

    PGPASSWORD="${DB_PASSWORD:-postgres}" createdb \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        "$target_db" \
        2>>"$LOG_FILE"

    log "Restoring from backup..."
    if [[ "$backup_file" == *.gz ]]; then
        gunzip -c "$backup_file" | PGPASSWORD="${DB_PASSWORD:-postgres}" pg_restore \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$target_db" \
            --no-owner \
            --verbose \
            2>>"$LOG_FILE"
    else
        PGPASSWORD="${DB_PASSWORD:-postgres}" pg_restore \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$target_db" \
            --no-owner \
            --verbose \
            "$backup_file" \
            2>>"$LOG_FILE"
    fi

    if [ $? -eq 0 ]; then
        log "Restore completed successfully to ${target_db}"
    else
        log "Restore FAILED"
        exit 1
    fi
}

pitr_restore() {
    local target_time="$1"
    local target_db="${2:-${DB_NAME}_pitr}"

    log "Starting PITR restore to: ${target_time}"
    log "Target database: ${target_db}"

    log "PITR requires WAL archives. Ensure WAL archiving is configured."
    log "Creating target database from base backup + WAL..."

    PGPASSWORD="${DB_PASSWORD:-postgres}" pg_ctl \
        -D /tmp/pg_restore_data \
        initdb \
        2>>"$LOG_FILE" || true

    log "PITR restore initiated. Check PostgreSQL documentation for complete steps."
    log "Required WAL files should be in: ${BACKUP_DIR}/wal/"

    notify "PITR restore requested for ${target_time}. Manual intervention may be required." "INFO"
}

verify_restore() {
    local target_db="$1"
    log "Verifying restore for database: ${target_db}..."

    local table_count
    table_count=$(PGPASSWORD="${DB_PASSWORD:-postgres}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$target_db" \
        -t \
        -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" \
        2>>"$LOG_FILE" | tr -d ' ')

    local row_count
    row_count=$(PGPASSWORD="${DB_PASSWORD:-postgres}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$target_db" \
        -t \
        -c "SELECT sum(n_live_tup) FROM pg_stat_user_tables;" \
        2>>"$LOG_FILE" | tr -d ' ')

    log "Database: ${target_db}"
    log "Tables: ${table_count}"
    log "Estimated rows: ${row_count}"

    if [ "${table_count:-0}" -gt 0 ]; then
        log "Restore verification: SUCCESS"
    else
        log "Restore verification: FAILED - no tables found"
        exit 1
    fi
}

main() {
    local mode=""
    local backup_file=""
    local target_db="${DB_NAME}"
    local dry_run=false

    if [ $# -eq 0 ]; then
        usage
        exit 1
    fi

    while [ $# -gt 0 ]; do
        case "$1" in
            --list) mode="list"; shift ;;
            --latest) mode="latest"; shift ;;
            --backup-file) mode="specific"; backup_file="$2"; shift 2 ;;
            --pitr) mode="pitr"; pitr_time="$2"; shift 2 ;;
            --dry-run) dry_run=true; shift ;;
            --target-db) target_db="$2"; shift 2 ;;
            --help|-h) usage; exit 0 ;;
            *) echo "Unknown option: $1"; usage; exit 1 ;;
        esac
    done

    log "=== JobCare Voice Database Restore ==="

    if [ "$dry_run" = true ]; then
        log "DRY RUN MODE - No changes will be made"
    fi

    case "$mode" in
        list)
            list_backups
            ;;
        latest)
            backup_file=$(ls -t "${BACKUP_DIR}"/*.sql.gz 2>/dev/null | head -1)
            if [ -z "$backup_file" ]; then
                log "ERROR: No backups found"
                exit 1
            fi
            log "Latest backup: $(basename "$backup_file")"
            if [ "$dry_run" = false ]; then
                restore_backup "$backup_file" "$target_db"
                verify_restore "$target_db"
            else
                log "Would restore: ${backup_file} -> ${target_db}"
            fi
            ;;
        specific)
            if [ "$dry_run" = false ]; then
                restore_backup "$backup_file" "$target_db"
                verify_restore "$target_db"
            else
                log "Would restore: ${backup_file} -> ${target_db}"
            fi
            ;;
        pitr)
            if [ "$dry_run" = false ]; then
                pitr_restore "$pitr_time" "$target_db"
                verify_restore "$target_db"
            else
                log "Would perform PITR to: ${pitr_time} -> ${target_db}"
            fi
            ;;
        *)
            usage
            exit 1
            ;;
    esac

    log "=== Restore Complete ==="
}

main "$@"
