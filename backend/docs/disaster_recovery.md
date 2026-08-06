# HomiQ Disaster Recovery Plan & Standard Operating Procedure

## Executive Summary
This document outlines the Standard Operating Procedures (SOP) for Disaster Recovery, Database Restores, and System Recovery for the HomiQ Smart House Maintenance Service Platform.

---

## Service Level Objectives
- **Recovery Point Objective (RPO)**: < 1 Hour (Maximum acceptable data loss window)
- **Recovery Time Objective (RTO)**: < 15 Minutes (Maximum acceptable service downtime)

---

## 1. Automated Backup Strategy

### Database Backups (PostgreSQL)
- **Frequency**: Daily at 02:00 UTC via Celery Beat & [`scripts/backup_db.sh`](file:///C:/Users/prath/OneDrive/Desktop/HomiQ/homiq/backend/scripts/backup_db.sh).
- **Format**: Compressed GZip SQL dump (`.sql.gz`) with SHA-256 checksums (`.sha256`).
- **Retention**: 7 daily backups retained locally/cloud storage.

### Cache & Session Backups (Redis)
- **Persistence**: Redis Append Only File (`AOF`) and RDB snapshots configured in [`docker-compose.prod.yml`](file:///C:/Users/prath/OneDrive/Desktop/HomiQ/homiq/backend/docker-compose.prod.yml).

---

## 2. Disaster Recovery Protocol

### Step 1: Execute Database Restoration
To restore PostgreSQL database from a known-good backup file:

```bash
bash scripts/restore_db.sh /var/backups/homiq/homiq_db_backup_YYYYMMDD_HHMMSS.sql.gz --force
```

### Step 2: Re-run Alembic Migrations
Verify schema alignment after database restoration:

```bash
alembic upgrade head
```

### Step 3: Verify Application Health Diagnostics
Verify system services via health endpoint:

```bash
curl -f http://localhost/health/detail
```

---

## 3. Incident Escalation & Response Contacts
- **DevOps Lead**: devops@homiq.com
- **Database Administrator**: dba@homiq.com
- **Security Incident Response**: security@homiq.com
