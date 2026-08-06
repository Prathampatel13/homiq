"""
Prometheus Metrics & Application Observability Instrumentation.
"""

from __future__ import annotations

import time
from typing import Dict

# Global Application Metrics Counters
_HTTP_REQUESTS_TOTAL: Dict[str, int] = {}
_HTTP_REQUEST_LATENCY_SUM: float = 0.0
_HTTP_REQUEST_LATENCY_COUNT: int = 0

_BOOKINGS_CREATED_TOTAL: int = 0
_BOOKINGS_COMPLETED_TOTAL: int = 0
_FAILED_LOGINS_TOTAL: int = 0


def record_http_request(method: str, endpoint: str, status_code: int, duration_seconds: float):
    """Record an incoming HTTP request for Prometheus metrics."""
    global _HTTP_REQUEST_LATENCY_SUM, _HTTP_REQUEST_LATENCY_COUNT
    key = f'method="{method}",endpoint="{endpoint}",status="{status_code}"'
    _HTTP_REQUESTS_TOTAL[key] = _HTTP_REQUESTS_TOTAL.get(key, 0) + 1
    _HTTP_REQUEST_LATENCY_SUM += duration_seconds
    _HTTP_REQUEST_LATENCY_COUNT += 1


def record_booking_created():
    """Increment booking created business counter."""
    global _BOOKINGS_CREATED_TOTAL
    _BOOKINGS_CREATED_TOTAL += 1


def record_booking_completed():
    """Increment booking completed business counter."""
    global _BOOKINGS_COMPLETED_TOTAL
    _BOOKINGS_COMPLETED_TOTAL += 1


def record_failed_login_metric():
    """Increment security failed login counter."""
    global _FAILED_LOGINS_TOTAL
    _FAILED_LOGINS_TOTAL += 1


def generate_prometheus_metrics_text() -> str:
    """Format and return application metrics in Prometheus text format."""
    lines = [
        "# HELP homiq_http_requests_total Total number of HTTP requests.",
        "# TYPE homiq_http_requests_total counter",
    ]
    for labels, count in _HTTP_REQUESTS_TOTAL.items():
        lines.append(f"homiq_http_requests_total{{{labels}}} {count}")

    lines.extend([
        "# HELP homiq_http_request_duration_seconds Total duration of HTTP requests.",
        "# TYPE homiq_http_request_duration_seconds summary",
        f"homiq_http_request_duration_seconds_sum {_HTTP_REQUEST_LATENCY_SUM:.4f}",
        f"homiq_http_request_duration_seconds_count {_HTTP_REQUEST_LATENCY_COUNT}",
        "# HELP homiq_bookings_created_total Total bookings created.",
        "# TYPE homiq_bookings_created_total counter",
        f"homiq_bookings_created_total {_BOOKINGS_CREATED_TOTAL}",
        "# HELP homiq_bookings_completed_total Total bookings completed.",
        "# TYPE homiq_bookings_completed_total counter",
        f"homiq_bookings_completed_total {_BOOKINGS_COMPLETED_TOTAL}",
        "# HELP homiq_security_failed_logins_total Total failed login attempts.",
        "# TYPE homiq_security_failed_logins_total counter",
        f"homiq_security_failed_logins_total {_FAILED_LOGINS_TOTAL}",
    ])

    return "\n".join(lines) + "\n"
