from __future__ import annotations

import os
from typing import Any

try:
    from celery import Celery
    from celery.schedules import crontab
    HAS_CELERY = True
except ImportError:
    HAS_CELERY = False

from app.core.config import settings

REDIS_BROKER_URL = getattr(settings, "REDIS_BROKER_URL", "redis://localhost:6379/0")
REDIS_RESULT_BACKEND = getattr(settings, "REDIS_RESULT_BACKEND", "redis://localhost:6379/1")

if HAS_CELERY:
    celery_app = Celery(
        "homiq_tasks",
        broker=REDIS_BROKER_URL,
        backend=REDIS_RESULT_BACKEND,
        include=["app.tasks.background"],
    )

    celery_app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=300,  # 5 minutes hard timeout
        task_soft_time_limit=240,  # 4 minutes soft timeout
        beat_schedule={
            "cleanup-expired-otps": {
                "task": "app.tasks.background.cleanup_expired_otps_task",
                "schedule": crontab(minute="*/5"),
            },
            "cleanup-expired-qr-codes": {
                "task": "app.tasks.background.cleanup_expired_qr_codes_task",
                "schedule": crontab(minute="*/15"),
            },
            "auto-cancel-expired-bookings": {
                "task": "app.tasks.background.auto_cancel_expired_bookings_task",
                "schedule": crontab(minute="*/30"),
            },
            "send-hourly-booking-reminders": {
                "task": "app.tasks.background.send_hourly_booking_reminders_task",
                "schedule": crontab(minute=0, hour="*"),
            },
            "generate-daily-reports": {
                "task": "app.tasks.background.generate_daily_report_task",
                "schedule": crontab(minute=0, hour=0),
            },
            "database-cleanup-daily": {
                "task": "app.tasks.background.database_cleanup_task",
                "schedule": crontab(minute=0, hour=2),
            },
            "generate-weekly-reports": {
                "task": "app.tasks.background.generate_weekly_report_task",
                "schedule": crontab(minute=0, hour=0, day_of_week="sunday"),
            },
            "generate-monthly-reports": {
                "task": "app.tasks.background.generate_monthly_report_task",
                "schedule": crontab(minute=0, hour=0, day_of_month=1),
            },
        },
    )
else:
    class DummyCelery:
        def task(self, *args: Any, **kwargs: Any):
            def decorator(func: Any):
                func.delay = lambda *a, **kw: func(*a, **kw)
                func.apply_async = lambda *a, **kw: func(*a, **kw)
                return func
            return decorator

    celery_app = DummyCelery()
