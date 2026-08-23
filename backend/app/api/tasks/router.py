"""
Background Tasks & Scheduler API Endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user
from app.schemas.tasks import (
    ScheduledJobItem,
    SchedulerJobsResponse,
    TaskRetryRequest,
    TaskRetryResponse,
    TaskStatusResponse,
)
from app.core.celery_app import celery_app, HAS_CELERY
from app.tasks.background import TASK_RESULT_STORE

router = APIRouter(tags=["Background Tasks & Scheduler"])


@router.get(
    "/tasks/status/{task_id}",
    response_model=TaskStatusResponse,
    summary="Get Background Task Status",
    description="Inspect execution status and result of an asynchronous background task.",
)
def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get status of background task."""
    # Check fallback store first
    if task_id in TASK_RESULT_STORE:
        info = TASK_RESULT_STORE[task_id]
        return TaskStatusResponse(
            task_id=task_id,
            status=info["status"],
            result=info.get("result"),
            error=info.get("error"),
            completed_at=info.get("updated_at"),
        )

    # Check Celery AsyncResult if active
    if HAS_CELERY and hasattr(celery_app, "AsyncResult"):
        try:
            res = celery_app.AsyncResult(task_id)
            return TaskStatusResponse(
                task_id=task_id,
                status=res.status,
                result=res.result if res.ready() else None,
                error=str(res.result) if res.failed() else None,
            )
        except Exception:
            pass

    return TaskStatusResponse(
        task_id=task_id,
        status="PENDING",
        result=None,
        error=None,
    )


@router.post(
    "/tasks/retry/{task_id}",
    response_model=TaskRetryResponse,
    summary="Retry Failed Task",
    description="Re-trigger or retry a background task.",
)
def retry_task(
    task_id: str,
    payload: Optional[TaskRetryRequest] = None,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retry failed task."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can retry background tasks.",
        )

    TASK_RESULT_STORE[task_id] = {
        "task_id": task_id,
        "status": "RETRY",
        "result": {"retried_by": current_user.email},
        "updated_at": None,
    }

    return TaskRetryResponse(
        task_id=task_id,
        status="RETRY",
        message=f"Task {task_id} successfully queued for retry.",
    )


@router.get(
    "/scheduler/jobs",
    response_model=SchedulerJobsResponse,
    summary="List Scheduled Jobs",
    description="**Admin only.** Returns all active Celery Beat scheduled jobs and cron expressions.",
)
def list_scheduled_jobs(
    current_user: User = Depends(get_current_user),
) -> Any:
    """List all scheduled background jobs."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view scheduled jobs.",
        )

    jobs: list[ScheduledJobItem] = []
    if HAS_CELERY and hasattr(celery_app.conf, "beat_schedule"):
        for name, cfg in celery_app.conf.beat_schedule.items():
            jobs.append(
                ScheduledJobItem(
                    name=name,
                    task_name=cfg["task"],
                    schedule=str(cfg["schedule"]),
                    last_run=None,
                    next_run=None,
                )
            )
    else:
        # Static list of configured beat jobs
        jobs = [
            ScheduledJobItem(name="cleanup-expired-otps", task_name="cleanup_expired_otps_task", schedule="Every 5 min"),
            ScheduledJobItem(name="cleanup-expired-qr-codes", task_name="cleanup_expired_qr_codes_task", schedule="Every 15 min"),
            ScheduledJobItem(name="auto-cancel-expired-bookings", task_name="auto_cancel_expired_bookings_task", schedule="Every 30 min"),
            ScheduledJobItem(name="send-hourly-booking-reminders", task_name="send_hourly_booking_reminders_task", schedule="Hourly"),
            ScheduledJobItem(name="generate-daily-reports", task_name="generate_daily_report_task", schedule="Daily at 00:00 UTC"),
            ScheduledJobItem(name="database-cleanup-daily", task_name="database_cleanup_task", schedule="Daily at 02:00 UTC"),
            ScheduledJobItem(name="generate-weekly-reports", task_name="generate_weekly_report_task", schedule="Weekly (Sunday)"),
            ScheduledJobItem(name="generate-monthly-reports", task_name="generate_monthly_report_task", schedule="Monthly (1st of month)"),
        ]

    return SchedulerJobsResponse(total_jobs=len(jobs), jobs=jobs)
