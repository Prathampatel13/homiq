#!/usr/bin/env bash
# ==============================================================================
# HomiQ Production Container Entrypoint Script
# ==============================================================================
set -e

echo "========================================================"
echo "Starting HomiQ Production Container Services"
echo "========================================================"

# Function to check database connectivity
wait_for_db() {
    echo "Checking PostgreSQL Database readiness..."
    python -c "
import sys, time
from sqlalchemy import create_engine
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
for i in range(30):
    try:
        with engine.connect() as conn:
            print('PostgreSQL Database is ready and accepting connections.')
            sys.exit(0)
    except Exception as e:
        print(f'Waiting for PostgreSQL... ({i+1}/30)')
        time.sleep(2)
sys.exit(1)
"
}

# Function to run Alembic database migrations
run_migrations() {
    echo "Running automatic Alembic database schema migrations..."
    alembic upgrade head
    echo "Alembic migrations completed successfully."
}

# Execute readiness check and migrations if running backend web service
if [ "$1" = "uvicorn" ] || [ "$1" = "gunicorn" ]; then
    wait_for_db
    run_migrations
fi

echo "Launching application process: $@"
exec "$@"
