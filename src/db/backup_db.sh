#!/usr/bin/env bash
# DEPRECATED: This script is no longer maintained.
# Use the Python management command instead: uv run python -m manage backup-db
# Database backup script for forensic evidence preservation
set -euo pipefail

DB_NAME="${CYBERSEC_DB_NAME:-cybersec_forensics}"
DB_HOST="${CYBERSEC_DB_HOST:-127.0.0.1}"
DB_PORT="${CYBERSEC_DB_PORT:-5432}"
DB_USER="${CYBERSEC_DB_USER:-cybersec}"
BACKUP_DIR="${CYBERSEC_BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

echo "Creating forensic database backup..."
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --create --clean --if-exists --verbose \
    --file="$BACKUP_DIR/cybersec_forensics_${TIMESTAMP}.sql"

gzip "$BACKUP_DIR/cybersec_forensics_${TIMESTAMP}.sql"
echo "Backup completed: $BACKUP_DIR/cybersec_forensics_${TIMESTAMP}.sql.gz"
