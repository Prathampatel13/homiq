# HomiQ Enterprise Backend System Architecture & Engineering Reference

## 1. System Overview & Technology Stack
**HomiQ** is an enterprise-grade Smart House Maintenance Service & Booking Platform. The backend is built using a clean 3-tier layered architecture powering high-throughput REST APIs, real-time WebSocket communication, background task processing, and robust enterprise security.

### Core Technology Stack
- **Web Framework**: FastAPI (Python 3.11)
- **Database & ORM**: PostgreSQL 16, SQLAlchemy 2.0, Alembic
- **Caching & Message Broker**: Redis 7, Celery, Celery Beat
- **Real-Time Engine**: WebSockets, Redis Pub/Sub
- **Integrations**: Razorpay Payment Gateway, Google Maps API, Cloudinary Media Engine, SMTP Email, SMS Gateway
- **Containerization & Web Server**: Docker, Docker Compose, Nginx Reverse Proxy
- **CI/CD**: GitHub Actions, GitHub Container Registry (`ghcr.io`)
- **Observability**: Prometheus Metrics (`/metrics`), Health Diagnostics (`/health/detail`)

---

## 2. Layered Software Architecture

```
                                 [ Client Applications / Mobile / Web ]
                                                   │
                                                   ▼
                                       [ Nginx Reverse Proxy ]
                                        (SSL/TLS, Rate Limit)
                                                   │
                                                   ▼
                                        [ FastAPI Web Node ]
                                   (Middleware, Security, CORS)
                                                   │
                                                   ▼
       ┌───────────────────────────────────────────┴───────────────────────────────────────────┐
       │                                                                                       │
       ▼                                                                                       ▼
[ REST API Routers ]                                                                 [ WebSocket Endpoints ]
(Thin Controllers)                                                                    (Real-time Streams)
       │                                                                                       │
       ▼                                                                                       ▼
[ Service Layer ]                                                                   [ WebSocket Service & Manager ]
(Business Logic, RBAC)                                                               (Room Routing, Pub/Sub)
       │                                                                                       │
       ▼                                                                                       ▼
[ Repository / CRUD Layer ]                                                          [ Redis Cache & Broker ]
(Encapsulated DB Queries)                                                             (Token Blacklist, Sessions)
       │                                                                                       │
       └───────────────────────────────────────────┬───────────────────────────────────────────┘
                                                   │
                                                   ▼
                                        [ PostgreSQL Database ]
                                      (Connection Pool: 20/10)
```

---

## 3. Implemented Enterprise Modules

| # | Module | Core Functionality | Primary Components |
|---|--------|--------------------|-------------------|
| 1 | **Authentication & Auth** | JWT Access & Refresh Tokens, Role Checks | `app/api/auth/router.py`, `app/security/` |
| 2 | **Booking Lifecycle** | State-machine booking transitions | `app/api/bookings/router.py`, `app/services/booking.py` |
| 3 | **Provider & Technician** | Job dispatch, profile & availability | `app/api/technician/router.py`, `app/crud/technician.py` |
| 4 | **Admin Control** | User management, job assignment, approvals | `app/api/admin/router.py`, `app/services/admin.py` |
| 5 | **SmartVerify QR** | Cryptographic QR generation & scan verification | `app/api/tracking/router.py`, `app/services/tracking.py` |
| 6 | **Razorpay Payment** | Order creation, webhook signatures, refund processing | `app/api/payments/router.py`, `app/services/payment.py` |
| 7 | **Google Maps** | Distance matrix, geocoding & ETA calculation | `app/services/maps.py`, `app/core/config.py` |
| 8 | **Notifications** | Multi-channel dispatch (Email, SMS, Push, In-App) | `app/api/notifications/router.py`, `app/crud/notification.py` |
| 9 | **Cloudinary Media** | Profile & document verification uploads | `app/api/media/router.py`, `app/services/media.py` |
| 10 | **Reports & Analytics** | Revenue charts, performance summaries, CSV/Excel export | `app/api/reports/router.py`, `app/crud/analytics.py` |
| 11 | **Search & Recommendation** | Autocomplete, multi-criteria search, matching engine | `app/api/search/router.py`, `app/services/search.py` |
| 12 | **Background Jobs** | Async task queue & Celery Beat periodic scheduler | `app/core/celery_app.py`, `app/tasks/background.py` |
| 13 | **Real-Time WebSockets** | Chat, GPS tracking stream, Admin live feed | `app/core/websockets.py`, `app/api/websocket/router.py` |
| 14 | **Enterprise Security** | Rate limiting, brute-force lockout, audit logging, headers | `app/security/`, `app/middleware/security.py` |
| 15 | **Monitoring & Metrics** | Prometheus metrics (`/metrics`), Health diagnostics | `app/core/metrics.py`, `app/api/monitoring/router.py` |
| 16 | **Disaster Recovery** | Automated `pg_dump` backup, SHA-256 integrity, restore script | `scripts/backup_db.sh`, `scripts/restore_db.sh` |
| 17 | **Optimization** | Connection pool tuning, GZip response compression, Redis cache | `app/database/session.py`, `app/core/cache.py` |
| 18 | **Containerization** | Multi-stage Dockerfile, docker-compose suite | `Dockerfile`, `docker-compose.prod.yml` |
| 19 | **CI/CD Pipeline** | GitHub Actions workflows for CI, CD, DB migration, releases | `.github/workflows/` |
| 20 | **Production Deployment** | Nginx SSL/TLS, zero-downtime deploy & rollback scripts | `nginx/nginx.prod.conf`, `scripts/deploy.sh` |

---

## 4. Security & Compliance Architecture
- **Authentication**: OAuth2 Password Flow + JWT (HS256 algorithm).
- **Token Blacklisting**: Revoked JWT `jti` identifiers stored in Redis (`homiq:blacklist:{jti}`).
- **Brute-Force Protection**: 5 consecutive failed login attempts lock account/IP for 15 minutes (`homiq:lockout:{identifier}`).
- **API Rate Limiting**: Sliding window rate limiter using Redis sorted sets (`homiq:ratelimit:{key}`).
- **Security Headers**: Enforced via `SecurityHeadersMiddleware` (`X-Frame-Options: DENY`, `nosniff`, CSP, HSTS).
- **Audit Logging**: Sensitive data masked (passwords, PINs, tokens, cards) before writing to PostgreSQL `audit_logs` table.
- **SQL Injection Defense**: Strict whitelist validation for dynamic `ORDER BY` fields & search wildcard escaping.

---

## 5. Real-Time WebSockets & Pub/Sub Routing Map

```
Client Connection                           Connection Manager                               Pub/Sub Channel
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
ws://.../ws/customer/{id}?token=...     ──> Customer Sockets Map         ──> homiq:events:customer:{id}
ws://.../ws/technician/{id}?token=...   ──> Technician Sockets Map       ──> homiq:events:technician:{id}
ws://.../ws/admin?token=...             ──> Admin Sockets Broadcast      ──> homiq:events:admin
ws://.../ws/chat/{booking_id}?token=... ──> Room: chat_{booking_id}      ──> homiq:chat:{booking_id}
ws://.../ws/location/{booking_id}?token ──> Room: location_{booking_id}  ──> homiq:location:{booking_id}
```

---

## 6. Celery Beat Periodic Task Cron Schedule

| Cron Schedule | Periodic Task Name | Target Function | Purpose |
|---------------|-------------------|-----------------|---------|
| Every 5 min | `cleanup-expired-otps` | `cleanup_expired_otps_task` | Delete stale OTP tokens |
| Every 15 min | `cleanup-expired-qr-codes` | `cleanup_expired_qr_codes_task` | Deactivate unverified QR codes |
| Every 30 min | `auto-cancel-expired-bookings` | `auto_cancel_expired_bookings_task` | Auto-cancel unassigned bookings |
| Every Hour | `send-hourly-booking-reminders` | `send_booking_reminder_task` | Dispatch service reminders |
| Daily 00:00 UTC | `generate-daily-reports` | `generate_daily_report_task` | Compile daily revenue metrics |
| Daily 02:00 UTC | `database-cleanup-daily` | `database_cleanup_task` & `backup_db.sh` | Purge audit logs & run DB backup |
| Weekly Sun 00:00 | `generate-weekly-reports` | `generate_weekly_report_task` | Compile weekly analytics |
| Monthly 1st 00:00 | `generate-monthly-reports` | `generate_monthly_report_task` | Compile monthly financial report |

---

## 7. Deployment & Infrastructure Layout

```
                                          [ Internet ]
                                               │
                                               ▼
                                      [ Nginx Port 80/443 ]
                                    (SSL Certbot, Rate Limit)
                                               │
                                 ┌─────────────┴─────────────┐
                                 │                           │
                                 ▼                           ▼
                        [ REST API: /api ]            [ WebSockets: /ws ]
                        (Pass to Backend)            (Upgrade Connection)
                                 │                           │
                                 └─────────────┬─────────────┘
                                               │
                                               ▼
                                   [ FastAPI Container: 8000 ]
                                               │
               ┌───────────────────────────────┼───────────────────────────────┐
               │                               │                               │
               ▼                               ▼                               ▼
    [ PostgreSQL Container ]          [ Redis Container ]           [ Celery Worker & Beat ]
      (Volume: postgres_data)           (Volume: redis_data)          (Async Background Tasks)
```

---

## 8. Verification & Operational Commands

### Run Full System Integration Test Suites:
```bash
# Run Security Tests
python scratch/test_enterprise_security_workflow.py

# Run Real-Time WebSocket Tests
python scratch/test_websocket_system_workflow.py

# Run Background Jobs Tests
python scratch/test_background_jobs_workflow.py

# Run Search & Recommendation Tests
python scratch/test_search_recommendations_workflow.py

# Run Monitoring, Backup & Performance Tests
python scratch/test_monitoring_backup_optimization_workflow.py
```

### Production Deployment Execution:
```bash
# Zero-Downtime Deployment
bash scripts/deploy.sh

# Emergency Automated Rollback
bash scripts/rollback.sh

# Manual Database Backup
bash scripts/backup_db.sh

# Database Restore
bash scripts/restore_db.sh /var/backups/homiq/homiq_db_backup_XXXX.sql.gz --force
```
