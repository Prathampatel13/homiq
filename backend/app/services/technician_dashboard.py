"""
Technician dashboard service.

Provides personalized dashboard data for technicians:
- Job statistics (assigned, accepted, in-progress, completed, cancelled)
- Earnings (total, pending)
- Ratings and reviews
- Today's jobs and next job
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.technician import TechnicianCRUD
from app.models.auth import User
from app.models.bookings import Booking, BookingStatus, PaymentStatus as BookingPayStatus
from app.models.payments import Payment, PaymentStatus as PayStatus
from app.models.reviews import Review
from app.schemas.dashboard import (
    RecentBookingResponse,
    TechnicianDashboardResponse,
    TechnicianDashboardStats,
)


class TechnicianDashboardService:
    """Service for technician dashboard aggregated data."""

    def __init__(self, db: Session):
        self.db = db
        self.technician_crud = TechnicianCRUD(db)

    def get_dashboard(self, current_user: User) -> TechnicianDashboardResponse:
        """Build the technician dashboard response."""
        technician = self.technician_crud.get_by_user_id(current_user.id)
        if not technician:
            return TechnicianDashboardResponse(stats=TechnicianDashboardStats())

        technician_id = technician.id

        # ── Job Stats ──────────────────────────────────────────────────
        total_assigned = self.db.scalar(
            select(func.count(Booking.id)).where(Booking.technician_id == technician_id)
        ) or 0
        accepted = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.technician_id == technician_id,
                Booking.status == BookingStatus.ACCEPTED,
            )
        ) or 0
        in_progress = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.technician_id == technician_id,
                Booking.status.in_([
                    BookingStatus.ON_THE_WAY,
                    BookingStatus.ARRIVED,
                    BookingStatus.WAITING_QR,
                    BookingStatus.QR_VERIFIED,
                    BookingStatus.IN_PROGRESS,
                ]),
            )
        ) or 0
        completed = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.technician_id == technician_id,
                Booking.status == BookingStatus.COMPLETED,
            )
        ) or 0
        cancelled = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.technician_id == technician_id,
                Booking.status == BookingStatus.CANCELLED,
            )
        ) or 0

        # ── Earnings ───────────────────────────────────────────────────
        total_earnings = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0))
                .join(Booking, Payment.booking_id == Booking.id)
                .where(
                    Booking.technician_id == technician_id,
                    Payment.status == PayStatus.PAID,
                )
            ) or 0.0
        )

        # Pending earnings = completed bookings not yet paid
        pending_earnings = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Booking.final_price), 0))
                .where(
                    Booking.technician_id == technician_id,
                    Booking.status == BookingStatus.COMPLETED,
                    Booking.payment_status == BookingPayStatus.PENDING,
                )
            ) or 0.0
        )

        # ── Ratings ────────────────────────────────────────────────────
        total_reviews = self.db.scalar(
            select(func.count(Review.id)).where(Review.technician_id == technician_id)
        ) or 0

        # Completion rate
        completion_rate = 0.0
        if total_assigned > 0:
            completion_rate = round((completed / total_assigned) * 100, 1)

        stats = TechnicianDashboardStats(
            total_assigned=total_assigned,
            accepted=accepted,
            in_progress=in_progress,
            completed=completed,
            cancelled=cancelled,
            total_earnings=round(total_earnings, 2),
            pending_earnings=round(pending_earnings, 2),
            average_rating=technician.rating,
            total_reviews=total_reviews,
            completion_rate=completion_rate,
        )

        # ── Today's Jobs ───────────────────────────────────────────────
        today_jobs = self._todays_jobs(technician_id)

        # ── Next Job ───────────────────────────────────────────────────
        next_job = self._next_job(technician_id)

        return TechnicianDashboardResponse(
            stats=stats,
            todays_jobs=today_jobs,
            next_job=next_job,
        )

    def _todays_jobs(self, technician_id: int, limit: int = 10) -> list[RecentBookingResponse]:
        stmt = (
            select(Booking)
            .where(
                Booking.technician_id == technician_id,
                Booking.booking_date == date.today(),
            )
            .order_by(Booking.preferred_time.asc(), Booking.created_at.desc())
            .limit(limit)
        )
        bookings = self.db.execute(stmt).scalars().all()
        result = []
        for booking in bookings:
            service_name = booking.service.name if booking.service else "N/A"
            customer_name = booking.customer.user.full_name if booking.customer and booking.customer.user else "N/A"
            amount = booking.final_price or booking.estimated_price or 0.0
            result.append(RecentBookingResponse(
                id=booking.id,
                booking_number=booking.booking_number,
                customer_name=customer_name,
                service_name=service_name,
                status=booking.status.value if hasattr(booking.status, 'value') else str(booking.status),
                amount=amount,
                created_at=booking.created_at,
            ))
        return result

    def _next_job(self, technician_id: int) -> RecentBookingResponse | None:
        stmt = (
            select(Booking)
            .where(
                Booking.technician_id == technician_id,
                Booking.status.in_([
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
        customer_name = booking.customer.user.full_name if booking.customer and booking.customer.user else "N/A"
        amount = booking.final_price or booking.estimated_price or 0.0
        return RecentBookingResponse(
            id=booking.id,
            booking_number=booking.booking_number,
            customer_name=customer_name,
            service_name=service_name,
            status=booking.status.value if hasattr(booking.status, 'value') else str(booking.status),
            amount=amount,
            created_at=booking.created_at,
        )
