"""
Admin management endpoints.

All endpoints are JWT-protected and require superuser/admin role.
Provides dashboard statistics, booking management, and system administration.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.models.bookings import BookingStatus
from app.security.deps import get_current_admin
from app.schemas.bookings import (
    BookingAssignTechnician,
    BookingListResponse,
    BookingResponse,
    BookingStatusUpdate,
)
from app.schemas.dashboard import AdminDashboardResponse
from app.schemas.services import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
)
from app.schemas.coupons import CouponCreate, CouponListResponse, CouponResponse, CouponUpdate
from app.schemas.invoices import InvoiceCreate, InvoiceListResponse, InvoiceResponse, InvoiceUpdate
from app.schemas.reviews import ReviewListResponse
from app.services.booking import BookingService
from app.services.admin_dashboard import AdminDashboardService
from app.services.service import ServiceService
from app.services.coupon import CouponService
from app.services.invoice import InvoiceService
from app.services.review import ReviewService
from app.services.report import ReportService
from app.services.analytics import AnalyticsService
from app.schemas.dashboard import (
    AnalyticsOverview,
    BookingAnalytics,
    CustomerAnalytics,
    RevenueAnalytics,
    BookingReport,
    RevenueReport,
    TechnicianReport,
    ReportFilter,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ═══════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════


@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse,
    summary="Admin dashboard",
    description=(
        "Returns comprehensive dashboard statistics for the admin panel. "
        "Includes revenue, booking counts, top services, top technicians, "
        "and recent bookings."
    ),
)
def get_dashboard(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Get admin dashboard with all statistics."""
    return AdminDashboardService(db).get_dashboard()


# ═══════════════════════════════════════════════════════════════════════
# BOOKING MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════


@router.get(
    "/bookings",
    response_model=BookingListResponse,
    summary="List all bookings",
    description="Returns a paginated list of all bookings in the system.",
)
def list_all_bookings(
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """List all bookings (admin view)."""
    return BookingService(db).list_bookings(current_user, offset=offset, limit=limit)


@router.get(
    "/bookings/{booking_id}",
    response_model=BookingResponse,
    summary="Get booking details",
    description="Returns full details of any booking by its ID.",
)
def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Get a booking by ID (admin view)."""
    return BookingService(db).get_booking(current_user, booking_id)


@router.put(
    "/bookings/{booking_id}/assign",
    response_model=BookingResponse,
    summary="Assign technician to booking",
    description="Assigns a technician to a booking. Booking must be in 'pending' status.",
)
def assign_technician(
    booking_id: int,
    payload: BookingAssignTechnician,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Assign a technician to a booking (admin only)."""
    return BookingService(db).assign_technician(current_user, booking_id, payload)


@router.put(
    "/bookings/{booking_id}/status",
    response_model=BookingResponse,
    summary="Update booking status",
    description="Updates the status of any booking. Admins can override the state machine.",
)
def update_booking_status(
    booking_id: int,
    payload: BookingStatusUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Update booking status (admin override)."""
    return BookingService(db).update_status(
        current_user, booking_id, payload.status, admin_note=payload.admin_note
    )


# ═══════════════════════════════════════════════════════════════════════
# SERVICE & CATEGORY MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════


@router.post(
    "/services",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a service",
    description="Creates a new service offering.",
)
def create_service(
    payload: ServiceCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Create a new service. Admin access required."""
    return ServiceService(db).create_service(current_user, payload)


@router.put(
    "/services/{service_id}",
    response_model=ServiceResponse,
    summary="Update a service",
    description="Updates an existing service's details.",
)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Update a service. Admin access required."""
    return ServiceService(db).update_service(current_user, service_id, payload)


@router.delete(
    "/services/{service_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a service",
    description="Deletes a service by its ID.",
)
def delete_service(
    service_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Delete a service. Admin access required."""
    return ServiceService(db).delete_service(current_user, service_id)


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a category",
    description="Creates a new service category.",
)
def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Create a new category. Admin access required."""
    return ServiceService(db).create_category(current_user, payload)


@router.put(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Update a category",
    description="Updates an existing category's details.",
)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Update a category. Admin access required."""
    return ServiceService(db).update_category(current_user, category_id, payload)


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a category",
    description="Deletes a category by its ID.",
)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Delete a category. Admin access required."""
    return ServiceService(db).delete_category(current_user, category_id)


# ═══════════════════════════════════════════════════════════════════════
# COUPON MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════


@router.post(
    "/coupons",
    response_model=CouponResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a coupon",
    description="Creates a new discount coupon.",
)
def create_coupon(
    payload: CouponCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Create a coupon. Admin access required."""
    return CouponService(db).create_coupon(current_user, payload)


@router.get(
    "/coupons",
    response_model=CouponListResponse,
    summary="List all coupons",
    description="Returns a paginated list of all coupons.",
)
def list_coupons(
    is_active: bool | None = None,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """List all coupons (admin view)."""
    return CouponService(db).list_coupons(is_active=is_active, offset=offset, limit=limit)


@router.put(
    "/coupons/{coupon_id}",
    response_model=CouponResponse,
    summary="Update a coupon",
    description="Updates an existing coupon's rules.",
)
def update_coupon(
    coupon_id: int,
    payload: CouponUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Update a coupon. Admin access required."""
    return CouponService(db).update_coupon(current_user, coupon_id, payload)


@router.delete(
    "/coupons/{coupon_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a coupon",
    description="Deletes a coupon by its ID.",
)
def delete_coupon(
    coupon_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Delete a coupon. Admin access required."""
    return CouponService(db).delete_coupon(current_user, coupon_id)


# ═══════════════════════════════════════════════════════════════════════
# INVOICE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════


@router.post(
    "/invoices",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an invoice",
    description="Creates a new invoice for a booking.",
)
def create_invoice(
    payload: InvoiceCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Create an invoice. Admin access required."""
    return InvoiceService(db).create_invoice(current_user, payload)


@router.get(
    "/invoices",
    response_model=InvoiceListResponse,
    summary="List all invoices",
    description="Returns a paginated list of all invoices.",
)
def list_invoices(
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """List all invoices (admin view)."""
    return InvoiceService(db).list_invoices(current_user, offset=offset, limit=limit)


@router.put(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Update an invoice",
    description="Updates an existing invoice.",
)
def update_invoice(
    invoice_id: int,
    payload: InvoiceUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Update an invoice. Admin access required."""
    return InvoiceService(db).update_invoice(current_user, invoice_id, payload)


@router.delete(
    "/invoices/{invoice_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an invoice",
    description="Deletes an invoice by its ID.",
)
def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Delete an invoice. Admin access required."""
    return InvoiceService(db).delete_invoice(current_user, invoice_id)


# ═══════════════════════════════════════════════════════════════════════
# REVIEW MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════


@router.get(
    "/reviews",
    response_model=ReviewListResponse,
    summary="List all reviews",
    description="Returns a paginated list of all reviews in the system.",
)
def list_all_reviews(
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """List all reviews (admin view)."""
    return ReviewService(db).list_reviews(offset=offset, limit=limit)


@router.delete(
    "/reviews/{review_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a review",
    description="Deletes a review by its ID. Admin override.",
)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Delete a review (admin override)."""
    return ReviewService(db).delete_review(current_user, review_id)


# ═══════════════════════════════════════════════════════════════════════
# REPORTS
# ═══════════════════════════════════════════════════════════════════════


@router.get(
    "/reports/revenue",
    response_model=RevenueReport,
    summary="Revenue report",
    description="Generates a comprehensive revenue report with breakdowns by service, month, and payment method.",
)
def get_revenue_report(
    start_date: str | None = None,
    end_date: str | None = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Generate a revenue report."""
    filters = ReportFilter(start_date=start_date, end_date=end_date)
    return ReportService(db).get_revenue_report(filters)


@router.get(
    "/reports/bookings",
    response_model=BookingReport,
    summary="Booking report",
    description="Generates a comprehensive booking report with breakdowns by status, service, and daily trends.",
)
def get_booking_report(
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
    service_id: int | None = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Generate a booking report."""
    booking_status = None
    if status:
        try:
            booking_status = BookingStatus(status)
        except ValueError:
            pass
    filters = ReportFilter(
        start_date=start_date,
        end_date=end_date,
        status=booking_status,
        service_id=service_id,
    )
    return ReportService(db).get_booking_report(filters)


@router.get(
    "/reports/technicians",
    response_model=list[TechnicianReport],
    summary="Technician performance report",
    description="Generates a technician performance report with booking and earnings metrics.",
)
def get_technician_report(
    technician_id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Generate a technician performance report."""
    filters = ReportFilter(start_date=start_date, end_date=end_date)
    return ReportService(db).get_technician_report(
        technician_id=technician_id,
        filters=filters,
    )


# ═══════════════════════════════════════════════════════════════════════
# ANALYTICS
# ═══════════════════════════════════════════════════════════════════════


@router.get(
    "/analytics/overview",
    response_model=AnalyticsOverview,
    summary="Analytics overview",
    description="Returns high-level analytics including total customers, bookings, revenue, and growth rates.",
)
def get_analytics_overview(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Get analytics overview."""
    return AnalyticsService(db).get_overview()


@router.get(
    "/analytics/customers",
    response_model=CustomerAnalytics,
    summary="Customer analytics",
    description="Returns detailed customer analytics including growth, active users, and city distribution.",
)
def get_customer_analytics(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Get customer analytics."""
    return AnalyticsService(db).get_customer_analytics()


@router.get(
    "/analytics/bookings",
    response_model=BookingAnalytics,
    summary="Booking analytics",
    description="Returns detailed booking analytics including trends, popular services, and peak hours.",
)
def get_booking_analytics(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Get booking analytics."""
    return AnalyticsService(db).get_booking_analytics()


@router.get(
    "/analytics/revenue",
    response_model=RevenueAnalytics,
    summary="Revenue analytics",
    description="Returns detailed revenue analytics including trends, payment method breakdown, and outstanding payments.",
)
def get_revenue_analytics(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Get revenue analytics."""
    return AnalyticsService(db).get_revenue_analytics()

