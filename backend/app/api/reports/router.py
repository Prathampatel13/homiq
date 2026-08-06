"""
Reports & Analytics API Endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user
from app.schemas.reports import (
    AdminAnalyticsFullResponse,
    CustomerAnalyticsResponse,
    ExportFormatEnum,
    PeriodReportResponse,
    TechnicianAnalyticsResponse,
)
from app.services.analytics import AnalyticsService

router = APIRouter(tags=["Reports & Analytics"])


@router.get(
    "/analytics/admin",
    response_model=AdminAnalyticsFullResponse,
    summary="Get admin analytics",
    description="**Admin only.** Returns high-level platform analytics (Users, Technicians, Bookings, Revenue, Popular Services, Peak Hours).",
)
def get_admin_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get full admin analytics."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access admin analytics.",
        )
    return AnalyticsService(db).get_full_admin_analytics()


@router.get(
    "/analytics/customer",
    response_model=CustomerAnalyticsResponse,
    summary="Get customer analytics",
    description="Returns personal analytics for the authenticated customer (Total bookings, completed, spent, favourite services).",
)
def get_customer_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get personal analytics for customer."""
    return AnalyticsService(db).get_customer_personal_analytics(current_user)


@router.get(
    "/analytics/technician",
    response_model=TechnicianAnalyticsResponse,
    summary="Get technician analytics",
    description="Returns personal performance metrics for the authenticated technician (Completed jobs, earnings, acceptance rate).",
)
def get_technician_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get personal analytics for technician."""
    return AnalyticsService(db).get_technician_personal_analytics(current_user)


# ─── TIME-PERIOD BUSINESS REPORTS ──────────────────────────────────────────


@router.get(
    "/reports/daily",
    response_model=PeriodReportResponse,
    summary="Get daily report",
    description="**Admin only.** Returns daily business metrics.",
)
def get_daily_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get daily business report."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return AnalyticsService(db).get_period_report("daily")


@router.get(
    "/reports/weekly",
    response_model=PeriodReportResponse,
    summary="Get weekly report",
    description="**Admin only.** Returns weekly business metrics.",
)
def get_weekly_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get weekly business report."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return AnalyticsService(db).get_period_report("weekly")


@router.get(
    "/reports/monthly",
    response_model=PeriodReportResponse,
    summary="Get monthly report",
    description="**Admin only.** Returns monthly business metrics.",
)
def get_monthly_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get monthly business report."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return AnalyticsService(db).get_period_report("monthly")


@router.get(
    "/reports/yearly",
    response_model=PeriodReportResponse,
    summary="Get yearly report",
    description="**Admin only.** Returns yearly business metrics.",
)
def get_yearly_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get yearly business report."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return AnalyticsService(db).get_period_report("yearly")


@router.get(
    "/reports/export",
    summary="Export reports",
    description="**Admin only.** Exports business report data as downloadable CSV, Excel, or PDF file.",
)
def export_reports(
    format: str = "csv",
    period: str = "monthly",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Export reports as downloadable CSV, Excel, or PDF."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return AnalyticsService(db).export_reports(format_type=format, period=period)
