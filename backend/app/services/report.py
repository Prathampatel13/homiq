"""
Report generation service.

Provides various reports for admin:
- Revenue reports
- Booking reports
- Technician performance reports
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.bookings import Booking, BookingStatus
from app.models.payments import Payment, PaymentStatus as PayStatus, PaymentMethod
from app.models.services import Service
from app.models.users import Technician
from app.models.reviews import Review
from app.schemas.dashboard import (
    BookingReport,
    RevenueReport,
    TechnicianReport,
    ReportFilter,
)


class ReportService:
    """Service for generating reports."""

    def __init__(self, db: Session):
        self.db = db

    def _apply_date_filter(self, stmt, column, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """Apply date range filter to a statement."""
        if start_date:
            try:
                start = datetime.fromisoformat(start_date)
                stmt = stmt.where(column >= start)
            except (ValueError, TypeError):
                pass
        if end_date:
            try:
                end = datetime.fromisoformat(end_date)
                stmt = stmt.where(column <= end)
            except (ValueError, TypeError):
                pass
        return stmt

    def get_revenue_report(self, filters: Optional[ReportFilter] = None) -> RevenueReport:
        """Generate a revenue report."""
        if filters is None:
            filters = ReportFilter()

        # Base payment query for paid payments
        base = select(Payment).where(Payment.status == PayStatus.PAID)
        base = self._apply_date_filter(base, Payment.created_at, filters.start_date, filters.end_date)

        # Total revenue
        total_revenue = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0))
                .where(Payment.status == PayStatus.PAID)
            ) or 0.0
        )

        # Total bookings that are paid
        total_bookings_paid = self.db.scalar(
            select(func.count(Payment.id)).where(Payment.status == PayStatus.PAID)
        ) or 0

        avg_order_value = round(total_revenue / total_bookings_paid, 2) if total_bookings_paid > 0 else 0.0

        # Revenue by service
        revenue_by_service = []
        services = self.db.execute(select(Service).where(Service.is_active.is_(True))).scalars().all()
        for svc in services:
            revenue = float(
                self.db.scalar(
                    select(func.coalesce(func.sum(Payment.amount), 0))
                    .join(Booking, Payment.booking_id == Booking.id)
                    .where(
                        Booking.service_id == svc.id,
                        Payment.status == PayStatus.PAID,
                    )
                ) or 0.0
            )
            count = self.db.scalar(
                select(func.count(Payment.id))
                .join(Booking, Payment.booking_id == Booking.id)
                .where(
                    Booking.service_id == svc.id,
                    Payment.status == PayStatus.PAID,
                )
            ) or 0
            if count > 0:
                revenue_by_service.append({
                    "service_name": svc.name,
                    "revenue": revenue,
                    "count": count,
                })

        # Revenue by month (last 12 months)
        from sqlalchemy import extract
        revenue_by_month = []
        now = datetime.now(timezone.utc)
        for i in range(11, -1, -1):
            month = (now.month - i - 1) % 12 + 1
            year = now.year + (now.month - i - 1) // 12
            month_name = datetime(year, month, 1).strftime("%b %Y")
            revenue = float(
                self.db.scalar(
                    select(func.coalesce(func.sum(Payment.amount), 0))
                    .where(
                        Payment.status == PayStatus.PAID,
                        extract("year", Payment.created_at) == year,
                        extract("month", Payment.created_at) == month,
                    )
                ) or 0.0
            )
            revenue_by_month.append({"month": month_name, "revenue": revenue})

        # Payment method breakdown
        payment_breakdown = []
        for method in PaymentMethod:
            count = self.db.scalar(
                select(func.count(Payment.id)).where(
                    Payment.payment_method == method,
                    Payment.status == PayStatus.PAID,
                )
            ) or 0
            if count > 0:
                payment_breakdown.append({
                    "method": method.value if hasattr(method, 'value') else str(method),
                    "count": count,
                })

        return RevenueReport(
            total_revenue=total_revenue,
            total_bookings=total_bookings_paid,
            average_order_value=avg_order_value,
            revenue_by_service=revenue_by_service,
            revenue_by_month=revenue_by_month,
            payment_method_breakdown=payment_breakdown,
        )

    def get_booking_report(self, filters: Optional[ReportFilter] = None) -> BookingReport:
        """Generate a booking report."""
        if filters is None:
            filters = ReportFilter()

        base = select(Booking)
        base = self._apply_date_filter(base, Booking.created_at, filters.start_date, filters.end_date)

        if filters.service_id:
            base = base.where(Booking.service_id == filters.service_id)
        if filters.status:
            base = base.where(Booking.status == filters.status)

        total = self.db.scalar(select(func.count()).select_from(base.subquery())) or 0
        completed = self.db.scalar(
            select(func.count(Booking.id)).where(Booking.status == BookingStatus.COMPLETED)
        ) or 0
        cancelled = self.db.scalar(
            select(func.count(Booking.id)).where(Booking.status == BookingStatus.CANCELLED)
        ) or 0
        pending = self.db.scalar(
            select(func.count(Booking.id)).where(Booking.status == BookingStatus.PENDING)
        ) or 0
        in_progress = self.db.scalar(
            select(func.count(Booking.id)).where(Booking.status == BookingStatus.IN_PROGRESS)
        ) or 0

        # Average completion time (in hours)
        avg_time = 0.0
        # Placeholder - actual calculation would need started_at/completed_at timestamps

        # Bookings by service
        bookings_by_service = []
        services = self.db.execute(select(Service)).scalars().all()
        for svc in services:
            count = self.db.scalar(
                select(func.count(Booking.id)).where(Booking.service_id == svc.id)
            ) or 0
            if count > 0:
                bookings_by_service.append({
                    "service_name": svc.name,
                    "count": count,
                })

        # Bookings by day (last 30 days)
        bookings_by_day = []
        now = datetime.now(timezone.utc)
        from datetime import timedelta
        for i in range(29, -1, -1):
            day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            day_start = (now - timedelta(days=i)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            day_end = day_start + timedelta(days=1)
            count = self.db.scalar(
                select(func.count(Booking.id)).where(
                    Booking.created_at >= day_start,
                    Booking.created_at < day_end,
                )
            ) or 0
            bookings_by_day.append({"date": day, "count": count})

        return BookingReport(
            total_bookings=total,
            completed=completed,
            cancelled=cancelled,
            pending=pending,
            in_progress=in_progress,
            average_completion_time_hours=avg_time,
            bookings_by_service=bookings_by_service,
            bookings_by_day=bookings_by_day,
        )

    def get_technician_report(
        self,
        technician_id: Optional[int] = None,
        filters: Optional[ReportFilter] = None,
    ) -> list[TechnicianReport]:
        """Generate a technician performance report."""
        if filters is None:
            filters = ReportFilter()

        stmt = select(Technician)
        if technician_id:
            stmt = stmt.where(Technician.id == technician_id)
        technicians = self.db.execute(stmt).scalars().all()

        results = []
        for tech in technicians:
            tech_booking_base = select(Booking).where(Booking.technician_id == tech.id)
            tech_booking_base = self._apply_date_filter(
                tech_booking_base, Booking.created_at, filters.start_date, filters.end_date
            )

            total = self.db.scalar(
                select(func.count(Booking.id)).where(Booking.technician_id == tech.id)
            ) or 0
            completed = self.db.scalar(
                select(func.count(Booking.id)).where(
                    Booking.technician_id == tech.id,
                    Booking.status == BookingStatus.COMPLETED,
                )
            ) or 0
            cancelled = self.db.scalar(
                select(func.count(Booking.id)).where(
                    Booking.technician_id == tech.id,
                    Booking.status == BookingStatus.CANCELLED,
                )
            ) or 0

            earnings = float(
                self.db.scalar(
                    select(func.coalesce(func.sum(Payment.amount), 0))
                    .join(Booking, Payment.booking_id == Booking.id)
                    .where(
                        Booking.technician_id == tech.id,
                        Payment.status == PayStatus.PAID,
                    )
                ) or 0.0
            )

            completion_rate = round((completed / total) * 100, 1) if total > 0 else 0.0

            results.append(TechnicianReport(
                technician_id=tech.id,
                technician_name=tech.user.full_name if tech.user else "Unknown",
                total_bookings=total,
                completed_bookings=completed,
                cancelled_bookings=cancelled,
                average_rating=tech.rating,
                total_earnings=earnings,
                completion_rate=completion_rate,
            ))

        return results

