"""
Monitoring, Prometheus Metrics, and Detailed Health Check Router.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import get_db

logger = logging.getLogger("homiq.monitoring")

router = APIRouter(tags=["System Monitoring & Health"])


@router.get(
    "/health/detail",
    summary="Detailed System Health Diagnostics",
    description="Inspects real-time connectivity and status for PostgreSQL Database, Redis Cache, and System Services.",
)
def get_detailed_health(
    db: Session = Depends(get_db),
) -> Any:
    """Detailed health check diagnostic endpoint."""
    health_status: dict[str, Any] = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {},
    }

    # 1. Check PostgreSQL Database
    try:
        start = time.time()
        db.execute(text("SELECT 1"))
        latency_ms = round((time.time() - start) * 1000, 2)
        health_status["services"]["database"] = {
            "status": "up",
            "latency_ms": latency_ms,
        }
    except Exception as exc:
        health_status["status"] = "unhealthy"
        health_status["services"]["database"] = {
            "status": "down",
            "error": str(exc),
        }

    # 2. Check Redis Cache
    try:
        from app.core.websockets import manager
        start = time.time()
        # Ping check via rate_limiter client if present
        from app.security.rate_limiter import rate_limiter
        if rate_limiter.redis_client:
            rate_limiter.redis_client.ping()
            latency_ms = round((time.time() - start) * 1000, 2)
            health_status["services"]["redis"] = {
                "status": "up",
                "latency_ms": latency_ms,
            }
        else:
            health_status["services"]["redis"] = {
                "status": "up (in-memory fallback)",
                "latency_ms": 0.0,
            }
    except Exception as exc:
        health_status["services"]["redis"] = {
            "status": "down",
            "error": str(exc),
        }

    # 3. WebSocket Active Connections Count
    try:
        from app.core.websockets import manager
        health_status["services"]["websockets"] = {
            "status": "up",
            "active_connections": len(manager.active_connections),
        }
    except Exception:
        pass

    http_status = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    return Response(
        content=str(health_status).replace("'", '"'),
        media_type="application/json",
        status_code=http_status,
    )


@router.get(
    "/metrics",
    summary="Prometheus Metrics Endpoint",
    description="Exposes application metrics for Prometheus scraping.",
)
def get_prometheus_metrics() -> Response:
    """Prometheus metrics endpoint."""
    from app.core.metrics import generate_prometheus_metrics_text
    metrics_data = generate_prometheus_metrics_text()
    return Response(
        content=metrics_data,
        media_type="text/plain; version=0.0.4",
    )
