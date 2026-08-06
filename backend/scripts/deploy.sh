#!/usr/bin/env bash
# ==============================================================================
# HomiQ Zero-Downtime Production Deployment Script
# ==============================================================================
set -e

echo "========================================================"
echo "Starting HomiQ Production Deployment"
echo "========================================================"

# Directory configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Ensure environment file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found in $PROJECT_ROOT"
    exit 1
fi

echo "[1/4] Pulling latest repository updates & Docker images..."
git pull origin main || true

echo "[2/4] Building production Docker images..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml build --parallel

echo "[3/4] Deploying updated container services..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --remove-orphans

echo "[4/4] Executing post-deployment health verification..."
HEALTH_URL="http://localhost/health"
MAX_ATTEMPTS=12
ATTEMPT=1
HEALTHY=false

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "Checking application health ($ATTEMPT/$MAX_ATTEMPTS)..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" || true)
    if [ "$HTTP_CODE" = "200" ]; then
        HEALTHY=true
        break
    fi
    sleep 5
    ATTEMPT=$((ATTEMPT + 1))
done

if [ "$HEALTHY" = true ]; then
    echo "========================================================"
    echo "DEPLOYMENT SUCCESSFUL! HomiQ application is healthy."
    echo "========================================================"
    exit 0
else
    echo "========================================================"
    echo "ERROR: Health check failed with status $HTTP_CODE!"
    echo "Triggering automated rollback script..."
    echo "========================================================"
    bash "$SCRIPT_DIR/rollback.sh"
    exit 1
fi
