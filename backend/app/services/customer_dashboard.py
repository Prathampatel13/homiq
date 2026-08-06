"""
Customer dashboard service.

Provides personalized dashboard data for customers:
- Booking statistics (total, active, completed, cancelled)
- Total spending and pending payments
- Recent and upcoming bookings
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.customer import CustomerCRUD
from app.models.auth import User
from app.models.bookings import Booking, BookingStatus, PaymentStatus as BookingPayStatus
from app.models.payments import Payment, PaymentStatus as PayStatus
from app.models.reviews import Review
from app.schemas.dashboard import (
    CustomerDashboardResponse,
    CustomerDashboardStats,
    RecentBookingResponse,
)


class CustomerDashboardService:
    """Service for customer dashboard aggregated data."""

    def __init__(self, db: Session):
        self.db = db
        self.customer_crud = CustomerCRUD(db)

    def get_dashboard(self, current_user: User) -> CustomerDashboardResponse:
        """Build the customer dashboard response."""
        customer = self.customer_crud.get_by_user_id(current_user.id)
        if not customer:
            return CustomerDashboardResponse(stats=CustomerDashboardStats())

        customer_id = customer.id

        # ── Booking Stats ──────────────────────────────────────────────
        total_bookings = self.db.scalar(
            select(func.count(Booking.id)).where(Booking.customer_id == customer_id)
        ) or 0
        active_bookings = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.customer_id == customer_id,
                Booking.status.in_([
                    BookingStatus.ASSIGNED,
                    BookingStatus.ACCEPTED,
                    BookingStatus.ON_THE_WAY,
                    BookingStatus.ARRIVED,
                    BookingStatus.WAITING_QR,
                    BookingStatus.QR_VERIFIED,
                    BookingStatus.IN_PROGRESS,
                ]),
            )
        ) or 0
        completed_bookings = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.customer_id == customer_id,
                Booking.status.in_([
                    BookingStatus.COMPLETED,
                    BookingStatus.WAITING_PAYMENT,
                    BookingStatus.PAID,
                    BookingStatus.REVIEW_PENDING,
                    BookingStatus.CLOSED,
                ]),
            )
        ) or 0
        cancelled_bookings = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.customer_id == customer_id,
                Booking.status.in_([
                    BookingStatus.CANCELLED,
                    BookingStatus.EXPIRED,
                    BookingStatus.REJECTED,
                ]),
            )
        ) or 0

        # ── Financial Stats ────────────────────────────────────────────
        total_spent = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.customer_id == customer_id,
                    Payment.status == PayStatus.PAID,
                )
            ) or 0.0
        )

        # Pending payments: bookings with pending payment_status
        pending_payments = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Booking.final_price), 0)).where(
                    Booking.customer_id == customer_id,
                    Booking.payment_status == BookingPayStatus.PENDING,
                    Booking.status == BookingStatus.COMPLETED,
                )
            ) or 0.0
        )

        total_reviews = self.db.scalar(
            select(func.count(Review.id)).where(Review.customer_id == customer_id)
        ) or 0

        now = datetime.now(timezone.utc)
        upcoming_bookings = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.customer_id == customer_id,
                Booking.booking_date >= now.date(),
                Booking.status.in_([
                    BookingStatus.PENDING,
                    BookingStatus.ASSIGNED,
                    BookingStatus.ACCEPTED,
                    BookingStatus.ON_THE_WAY,
                    BookingStatus.ARRIVED,
                    BookingStatus.WAITING_QR,
                    BookingStatus.QR_VERIFIED,
                ]),
            )
        ) or 0

        stats = CustomerDashboardStats(
            total_bookings=total_bookings,
            active_bookings=active_bookings,
            completed_bookings=completed_bookings,
            cancelled_bookings=cancelled_bookings,
            total_spent=round(total_spent, 2),
            pending_payments=round(pending_payments, 2),
            total_reviews=total_reviews,
            upcoming_bookings=upcoming_bookings,
        )

        # ── Recent Bookings ────────────────────────────────────────────
        recent = self._recent_bookings(customer_id)
        upcoming = self._upcoming_booking(customer_id)

        return CustomerDashboardResponse(
            stats=stats,
            recent_bookings=recent,
            upcoming_booking=upcoming,
        )

    def _recent_bookings(self, customer_id: int, limit: int = 5) -> list[RecentBookingResponse]:
        stmt = (
            select(Booking)
            .where(Booking.customer_id == customer_id)
            .order_by(Booking.created_at.desc())
            .limit(limit)
        )
        bookings = self.db.execute(stmt).scalars().all()
        result = []
        for booking in bookings:
            service_name = booking.service.name if booking.service else "N/A"
            amount = booking.final_price or booking.estimated_price or 0.0
            result.append(RecentBookingResponse(
                id=booking.id,
                booking_number=booking.booking_number,
                customer_name=booking.customer.user.full_name if booking.customer and booking.customer.user else "N/A",
                service_name=service_name,
                status=booking.status.value if hasattr(booking.status, 'value') else str(booking.status),
                amount=amount,
                created_at=booking.created_at,
            ))
        return result

    def _upcoming_booking(self, customer_id: int) -> RecentBookingResponse | None:
        from datetime import date

        stmt = (
            select(Booking)
            .where(
                Booking.customer_id == customer_id,
                Booking.booking_date >= date.today(),
                Booking.status.in_([
                    BookingStatus.PENDING,
                    BookingStatus.ASSIGNED,
                    BookingStatus.ACCEPTED,
                    BookingStatus.ON_THE_WAY,
                    BookingStatus.ARRIVED,
                    BookingStatus.WAITING_QR,
                    BookingStatus.QR_VERIFIED,
                ]),
            )
            .order_by(Booking.booking_date.asc(), Booking.preferred_time.asc())
            .limit(1)
        )
        booking = self.db.scalar(stmt)
        if not booking:
            return None
        service_name = booking.service.name if booking.service else "N/A"
        amount = booking.final_price or booking.estimated_price or 0.0
        return RecentBookingResponse(
            id=booking.id,
            booking_number=booking.booking_number,
            customer_name=booking.customer.user.full_name if booking.customer and booking.customer.user else "N/A",
            service_name=service_name,
            status=booking.status.value if hasattr(booking.status, 'value') else str(booking.status),
            amount=amount,
            created_at=booking.created_at,
        )

