#!/usr/bin/env bash
# start_prod.sh
# Runs migrations, Celery worker, and FastAPI in one container for a FREE tier deployment.

set -e

echo "Running Database Migrations..."
alembic upgrade head

echo "Starting Celery Worker in background..."
celery -A app.core.celery_app worker --loglevel=info &

# Optional: celery beat
# celery -A app.core.celery_app beat --loglevel=info &

echo "Starting FastAPI Server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
