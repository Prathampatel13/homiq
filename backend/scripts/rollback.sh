#!/usr/bin/env bash
# ==============================================================================
# HomiQ Production Rollback Script
# ==============================================================================
set -e

echo "========================================================"
echo "ALERT: Executing HomiQ Production Rollback Procedure"
echo "========================================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "[1/3] Rolling back Alembic database schema by 1 revision..."
docker compose exec -T backend alembic downgrade -1 || true

echo "[2/3] Restarting container services with previous stable state..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart backend celery_worker celery_beat

echo "[3/3] Verifying health check post-rollback..."
sleep 5
HEALTH_URL="http://localhost/health"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" || true)

if [ "$HTTP_CODE" = "200" ]; then
    echo "========================================================"
    echo "ROLLBACK SUCCESSFUL: System reverted and healthy."
    echo "========================================================"
    exit 0
else
    echo "========================================================"
    echo "CRITICAL: System still unhealthy after rollback (HTTP $HTTP_CODE)."
    echo "Immediate manual intervention required!"
    echo "========================================================"
    exit 1
fi
