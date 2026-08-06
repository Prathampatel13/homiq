#!/usr/bin/env bash
# ==============================================================================
# HomiQ Automated PostgreSQL Backup & Disaster Recovery Script
# ==============================================================================
set -e

BACKUP_DIR="${BACKUP_DIR:-/var/backups/homiq}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILENAME="homiq_db_backup_${TIMESTAMP}.sql.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILENAME}"

POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-homiq_db}"
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

echo "========================================================"
echo "Starting HomiQ Database Backup Process"
echo "Timestamp: ${TIMESTAMP}"
echo "========================================================"

# Ensure backup directory exists
mkdir -p "${BACKUP_DIR}"

# Run non-blocking compressed database dump
echo "[1/3] Dumping PostgreSQL database '${POSTGRES_DB}'..."
PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --no-owner --no-privileges | gzip -9 > "${BACKUP_PATH}"

# Generate SHA-256 Checksum
echo "[2/3] Generating checksum for backup verification..."
sha256sum "${BACKUP_PATH}" > "${BACKUP_PATH}.sha256"

# Rotate old backups (Retain backups for 7 days)
echo "[3/3] Enforcing backup retention policy (Cleaning backups older than 7 days)..."
find "${BACKUP_DIR}" -name "homiq_db_backup_*.sql.gz*" -type f -mtime +7 -delete

echo "========================================================"
echo "BACKUP SUCCESSFUL: ${BACKUP_PATH}"
echo "Checksum: $(cat "${BACKUP_PATH}.sha256")"
echo "========================================================"
