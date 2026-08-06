#!/usr/bin/env bash
# ==============================================================================
# HomiQ Database Restoration & Disaster Recovery Script
# ==============================================================================
set -e

BACKUP_FILE="$1"
CONFIRM_FLAG="$2"

POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-homiq_db}"
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <path_to_backup.sql.gz> [--force]"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file '$BACKUP_FILE' not found!"
    exit 1
fi

if [ "$CONFIRM_FLAG" != "--force" ]; then
    echo "WARNING: Restoring database will OVERWRITE existing data in '${POSTGRES_DB}'."
    read -p "Are you sure you want to proceed? (type 'RESTORE' to confirm): " CONFIRM
    if [ "$CONFIRM" != "RESTORE" ]; then
        echo "Restoration cancelled."
        exit 0
    fi
fi

# Verify SHA256 checksum if checksum file exists
if [ -f "${BACKUP_FILE}.sha256" ]; then
    echo "[1/3] Verifying SHA-256 checksum integrity..."
    sha256sum -c "${BACKUP_FILE}.sha256" || { echo "ERROR: Checksum mismatch!"; exit 1; }
fi

echo "[2/3] Preparing database target '${POSTGRES_DB}'..."
PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -c "DROP DATABASE IF EXISTS ${POSTGRES_DB}_restore_temp;" || true
PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -c "CREATE DATABASE ${POSTGRES_DB}_restore_temp;" || true

echo "[3/3] Restoring database from '${BACKUP_FILE}'..."
gunzip -c "${BACKUP_FILE}" | PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"

echo "========================================================"
echo "RESTORATION SUCCESSFUL: Database '${POSTGRES_DB}' restored."
echo "========================================================"
