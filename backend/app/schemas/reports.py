from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ExportFormatEnum(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"


class PeriodReportTypeEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class PopularServiceItem(BaseModel):
    service_name: str
    count: int


class PeakHourItem(BaseModel):
    hour: str
    count: int


class TopTechnicianItem(BaseModel):
    technician_id: int
    full_name: str
    completed_jobs: int
    rating: float


class AdminAnalyticsFullResponse(BaseModel):
    # User Metrics
    total_users: int = 0
    new_users: int = 0
    active_users: int = 0
    inactive_users: int = 0

    # Technician Metrics
    total_technicians: int = 0
    verified_technicians: int = 0
    pending_verification: int = 0
    online_technicians: int = 0
    offline_technicians: int = 0

    # Booking Metrics
    todays_bookings: int = 0
    weekly_bookings: int = 0
    monthly_bookings: int = 0
    cancelled_bookings: int = 0
    completed_bookings: int = 0
    pending_bookings: int = 0

    # Financial & Quality Metrics
    revenue: float = 0.0
    refunds: float = 0.0
    coupons_used: int = 0
    average_rating: float = 0.0

    # Trends & Lists
    popular_services: list[PopularServiceItem] = []
    peak_hours: list[PeakHourItem] = []
    top_technicians: list[TopTechnicianItem] = []

    model_config = {"from_attributes": True}


class CustomerAnalyticsResponse(BaseModel):
    total_bookings: int = 0
    completed_jobs: int = 0
    cancelled_jobs: int = 0
    total_spent: float = 0.0
    favourite_services: list[PopularServiceItem] = []
    reviews_count: int = 0

    model_config = {"from_attributes": True}


class TechnicianAnalyticsResponse(BaseModel):
    completed_jobs: int = 0
    pending_jobs: int = 0
    monthly_earnings: float = 0.0
    average_rating: float = 0.0
    acceptance_rate: float = 0.0
    cancellation_rate: float = 0.0
    working_hours: str = "9:00 AM - 6:00 PM"

    model_config = {"from_attributes": True}


class PeriodReportResponse(BaseModel):
    period_type: str
    start_date: str
    end_date: str
    total_bookings: int = 0
    completed_bookings: int = 0
    cancelled_bookings: int = 0
    total_revenue: float = 0.0
    new_customers: int = 0
    details: list[dict[str, Any]] = []

    model_config = {"from_attributes": True}
