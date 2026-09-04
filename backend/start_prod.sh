#!/usr/bin/env bash
# ==============================================================================
# HomiQ Production Startup Script (Free Tier Optimized)
# Runs Alembic migrations then starts FastAPI via Uvicorn.
# Redis/Celery are NOT required — the app uses in-memory fallbacks.
# ==============================================================================
set -e

echo "========================================================"
echo "HomiQ Backend — Starting Production Server"
echo "========================================================"

echo "[1/2] Running database migrations..."
alembic upgrade head || echo "Warning: Alembic migrations skipped (may already be up to date)"

echo "[2/2] Starting FastAPI server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
