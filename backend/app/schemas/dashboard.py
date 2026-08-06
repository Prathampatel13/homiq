from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Admin Dashboard ────────────────────────────────────────────────────


class AdminDashboardStats(BaseModel):
    total_revenue: float = 0.0
    total_customers: int = 0
    total_users: int = 0
    total_bookings: int = 0
    pending_jobs: int = 0
    completed_jobs: int = 0
    pending_bookings: int = 0
    active_bookings: int = 0
    completed_bookings: int = 0
    cancelled_bookings: int = 0
    total_technicians: int = 0
    pending_technicians: int = 0
    verified_technicians: int = 0
    active_technicians: int = 0
    total_services: int = 0
    total_categories: int = 0
    average_rating: float = 0.0
    todays_bookings: int = 0
    revenue_today: float = 0.0
    revenue_this_month: float = 0.0
    revenue_growth_percent: float = 0.0
    booking_growth_percent: float = 0.0


class RevenueChartData(BaseModel):
    labels: list[str]
    values: list[float]


class BookingStatusDistribution(BaseModel):
    status: str
    count: int


class TopServiceResponse(BaseModel):
    service_id: int
    service_name: str
    booking_count: int
    revenue: float


class TopTechnicianResponse(BaseModel):
    technician_id: int
    technician_name: str
    booking_count: int
    revenue: float
    rating: float


class RecentBookingResponse(BaseModel):
    id: int
    booking_number: str
    customer_name: str
    service_name: str
    status: str
    amount: float
    created_at: datetime


class AdminDashboardResponse(BaseModel):
    stats: AdminDashboardStats
    revenue_chart: Optional[RevenueChartData] = None
    booking_status_distribution: list[BookingStatusDistribution] = []
    top_services: list[TopServiceResponse] = []
    top_technicians: list[TopTechnicianResponse] = []
    recent_bookings: list[RecentBookingResponse] = []

    model_config = {"from_attributes": True}


# ── Admin User & Technician Management ───────────────────────────────


class AdminUserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminUserListResponse(BaseModel):
    items: list[AdminUserResponse]
    total: int


class AdminUserDetailResponse(BaseModel):
    user: AdminUserResponse
    total_bookings: int = 0
    total_spent: float = 0.0
    recent_bookings: list[RecentBookingResponse] = []


class TechnicianDocumentResponse(BaseModel):
    technician_id: int
    user_id: int
    full_name: str
    profile_image: Optional[str] = None
    government_id_image: Optional[str] = None
    is_verified: bool


class BookingStatusLogResponse(BaseModel):
    id: int
    booking_id: int
    old_status: Optional[str] = None
    new_status: str
    changed_by_user_id: Optional[int] = None
    reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── System Settings ────────────────────────────────────────────────────


class AdminSettingsResponse(BaseModel):
    platform_name: str = "HomiQ"
    support_email: str = "support@homiq.com"
    support_phone: str = "+1-800-HOMIQ"
    commission_percentage: float = 10.0
    tax_percentage: float = 18.0
    working_hours: str = "08:00 AM - 08:00 PM"
    max_active_bookings_per_technician: int = 1
    cancellation_window_hours: int = 2


class AdminSettingsUpdate(BaseModel):
    platform_name: Optional[str] = Field(None, max_length=255)
    support_email: Optional[str] = Field(None, max_length=255)
    support_phone: Optional[str] = Field(None, max_length=50)
    commission_percentage: Optional[float] = Field(None, ge=0, le=100)
    tax_percentage: Optional[float] = Field(None, ge=0, le=100)
    working_hours: Optional[str] = Field(None, max_length=255)
    max_active_bookings_per_technician: Optional[int] = Field(None, ge=1, le=50)
    cancellation_window_hours: Optional[int] = Field(None, ge=0, le=72)



# ── Customer Dashboard ─────────────────────────────────────────────────


class CustomerDashboardStats(BaseModel):
    total_bookings: int = 0
    active_bookings: int = 0
    completed_bookings: int = 0
    cancelled_bookings: int = 0
    total_spent: float = 0.0
    pending_payments: float = 0.0
    total_reviews: int = 0
    upcoming_bookings: int = 0


class CustomerDashboardResponse(BaseModel):
    stats: CustomerDashboardStats
    recent_bookings: list[RecentBookingResponse] = []
    upcoming_booking: Optional[RecentBookingResponse] = None

    model_config = {"from_attributes": True}


# ── Technician Dashboard ──────────────────────────────────────────────


class TechnicianDashboardStats(BaseModel):
    total_assigned: int = 0
    accepted: int = 0
    in_progress: int = 0
    completed: int = 0
    cancelled: int = 0
    total_earnings: float = 0.0
    pending_earnings: float = 0.0
    average_rating: float = 0.0
    total_reviews: int = 0
    completion_rate: float = 0.0


class TechnicianDashboardResponse(BaseModel):
    stats: TechnicianDashboardStats
    todays_jobs: list[RecentBookingResponse] = []
    next_job: Optional[RecentBookingResponse] = None

    model_config = {"from_attributes": True}


# ── Reports ────────────────────────────────────────────────────────────


class ReportFilter(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    technician_id: Optional[int] = None
    customer_id: Optional[int] = None
    service_id: Optional[int] = None
    status: Optional[str] = None


class RevenueReport(BaseModel):
    total_revenue: float = 0.0
    total_bookings: int = 0
    average_order_value: float = 0.0
    revenue_by_service: list[dict] = []
    revenue_by_month: list[dict] = []
    payment_method_breakdown: list[dict] = []

    model_config = {"from_attributes": True}


class BookingReport(BaseModel):
    total_bookings: int = 0
    completed: int = 0
    cancelled: int = 0
    pending: int = 0
    in_progress: int = 0
    average_completion_time_hours: float = 0.0
    bookings_by_service: list[dict] = []
    bookings_by_day: list[dict] = []

    model_config = {"from_attributes": True}


class TechnicianReport(BaseModel):
    technician_id: int
    technician_name: str
    total_bookings: int
    completed_bookings: int
    cancelled_bookings: int
    average_rating: float
    total_earnings: float
    completion_rate: float
    average_response_time_minutes: Optional[float] = None

    model_config = {"from_attributes": True}


# ── Analytics ──────────────────────────────────────────────────────────


class AnalyticsOverview(BaseModel):
    total_customers: int = 0
    total_technicians: int = 0
    total_bookings: int = 0
    total_revenue: float = 0.0
    total_services: int = 0
    average_rating: float = 0.0
    customer_growth_percent: float = 0.0
    booking_growth_percent: float = 0.0
    revenue_growth_percent: float = 0.0


class CustomerAnalytics(BaseModel):
    total_customers: int
    new_customers_this_month: int
    active_customers: int
    average_bookings_per_customer: float
    customer_growth_rate: float
    customer_by_city: list[dict] = []
    customer_registration_trend: list[dict] = []

    model_config = {"from_attributes": True}


class BookingAnalytics(BaseModel):
    total: int
    completed: int
    cancelled: int
    pending: int
    in_progress: int
    average_booking_value: float
    booking_trend: list[dict] = []
    popular_services: list[dict] = []
    peak_hours: list[dict] = []

    model_config = {"from_attributes": True}


class RevenueAnalytics(BaseModel):
    total_revenue: float
    revenue_this_month: float
    revenue_today: float
    average_revenue_per_booking: float
    monthly_revenue_trend: list[dict] = []
    revenue_by_payment_method: list[dict] = []
    outstanding_payments: float = 0.0

    model_config = {"from_attributes": True}

