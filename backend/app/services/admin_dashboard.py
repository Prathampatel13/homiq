"""
Admin dashboard service.

Provides aggregate data for the admin dashboard:
- Revenue statistics (total, today, this month, growth)
- Booking counts by status
- Top services and technicians
- Recent bookings
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.bookings import Booking, BookingStatus
from app.models.users import Customer, Technician
from app.models.services import Service, Category
from app.models.payments import Payment, PaymentStatus as PayStatus
from app.models.reviews import Review
from app.schemas.dashboard import (
    AdminDashboardResponse,
    AdminDashboardStats,
    BookingStatusDistribution,
    RecentBookingResponse,
    RevenueChartData,
    TopServiceResponse,
    TopTechnicianResponse,
)


class AdminDashboardService:
    """Service for admin dashboard aggregated data."""

    def __init__(self, db: Session):
        self.db = db

    def get_dashboard(self) -> AdminDashboardResponse:
        """
        Build the complete admin dashboard response with all statistics.
        """
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = today_start.replace(day=1)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)

        # ── Core Counts ────────────────────────────────────────────────
        total_revenue = self._total_revenue()
        total_customers = self.db.scalar(select(func.count(Customer.id))) or 0
        total_bookings = self.db.scalar(select(func.count(Booking.id))) or 0
        pending_jobs = self.db.scalar(
            select(func.count(Booking.id)).where(Booking.status == BookingStatus.PENDING)
        ) or 0
        completed_jobs = self.db.scalar(
            select(func.count(Booking.id)).where(Booking.status == BookingStatus.COMPLETED)
        ) or 0
        total_technicians = self.db.scalar(select(func.count(Technician.id))) or 0
        active_technicians = self.db.scalar(
            select(func.count(Technician.id)).where(Technician.availability.is_(True))
        ) or 0
        total_services = self.db.scalar(select(func.count(Service.id))) or 0
        total_categories = self.db.scalar(select(func.count(Category.id))) or 0

        avg_rating = self.db.scalar(select(func.avg(Review.rating))) or 0.0

        # ── Today & Monthly Revenue ────────────────────────────────────
        revenue_today = self._revenue_in_range(today_start, now)
        revenue_this_month = self._revenue_in_range(month_start, now)
        revenue_last_month = self._revenue_in_range(last_month_start, month_start)

        revenue_growth = 0.0
        if revenue_last_month > 0:
            revenue_growth = ((revenue_this_month - revenue_last_month) / revenue_last_month) * 100

        # ── Booking Growth ─────────────────────────────────────────────
        bookings_this_month = self.db.scalar(
            select(func.count(Booking.id)).where(Booking.created_at >= month_start)
        ) or 0
        bookings_last_month = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.created_at >= last_month_start,
                Booking.created_at < month_start,
            )
        ) or 0
        booking_growth = 0.0
        if bookings_last_month > 0:
            booking_growth = ((bookings_this_month - bookings_last_month) / bookings_last_month) * 100

        stats = AdminDashboardStats(
            total_revenue=total_revenue,
            total_customers=total_customers,
            total_bookings=total_bookings,
            pending_jobs=pending_jobs,
            completed_jobs=completed_jobs,
            total_technicians=total_technicians,
            active_technicians=active_technicians,
            total_services=total_services,
            total_categories=total_categories,
            average_rating=round(float(avg_rating), 2),
            todays_bookings=self.db.scalar(
                select(func.count(Booking.id)).where(Booking.created_at >= today_start)
            ) or 0,
            revenue_today=revenue_today,
            revenue_this_month=revenue_this_month,
            revenue_growth_percent=round(revenue_growth, 1),
            booking_growth_percent=round(booking_growth, 1),
        )

        # ── Revenue Chart (last 12 months) ─────────────────────────────
        revenue_chart = self._revenue_chart()

        # ── Booking Status Distribution ────────────────────────────────
        status_distribution = self._booking_status_distribution()

        # ── Top Services ───────────────────────────────────────────────
        top_services = self._top_services()

        # ── Top Technicians ────────────────────────────────────────────
        top_technicians = self._top_technicians()

        # ── Recent Bookings ────────────────────────────────────────────
        recent_bookings = self._recent_bookings()

        return AdminDashboardResponse(
            stats=stats,
            revenue_chart=revenue_chart,
            booking_status_distribution=status_distribution,
            top_services=top_services,
            top_technicians=top_technicians,
            recent_bookings=recent_bookings,
        )

    def _total_revenue(self) -> float:
        """Calculate total revenue from paid payments."""
        result = self.db.scalar(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.status == PayStatus.PAID
            )
        )
        return float(result or 0.0)

    def _revenue_in_range(self, start: datetime, end: datetime) -> float:
        """Calculate revenue within a date range."""
        result = self.db.scalar(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.status == PayStatus.PAID,
                Payment.created_at >= start,
                Payment.created_at <= end,
            )
        )
        return float(result or 0.0)

    def _revenue_chart(self) -> RevenueChartData:
        """Get monthly revenue for the last 12 months."""
        from sqlalchemy import extract

        labels = []
        values = []
        now = datetime.now(timezone.utc)
        for i in range(11, -1, -1):
            month = (now.month - i - 1) % 12 + 1
            year = now.year + (now.month - i - 1) // 12
            month_name = date(year, month, 1).strftime("%b %Y")

            start = datetime(year, month, 1, tzinfo=timezone.utc)
            if month == 12:
                end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                end = datetime(year, month + 1, 1, tzinfo=timezone.utc)

            revenue = self._revenue_in_range(start, end)
            labels.append(month_name)
            values.append(revenue)

        return RevenueChartData(labels=labels, values=values)

    def _booking_status_distribution(self) -> list[BookingStatusDistribution]:
        """Get breakdown of bookings by status."""
        from sqlalchemy import func
        stmt = (
            select(Booking.status, func.count(Booking.id).label("count"))
            .group_by(Booking.status)
            .order_by(Booking.status)
        )
        results = self.db.execute(stmt).all()
        return [BookingStatusDistribution(status=str(row[0]), count=row[1]) for row in results]

    def _top_services(self, limit: int = 5) -> list[TopServiceResponse]:
        """Get top services by booking count and revenue."""
        from app.models.payments import Payment
        from sqlalchemy import func

        stmt = (
            select(
                Booking.service_id,
                func.count(Booking.id).label("booking_count"),
                func.coalesce(func.sum(Payment.amount), 0).label("revenue"),
            )
            .join(Payment, Payment.booking_id == Booking.id)
            .where(Payment.status == PayStatus.PAID)
            .group_by(Booking.service_id)
            .order_by(func.count(Booking.id).desc())
            .limit(limit)
        )
        results = self.db.execute(stmt).all()
        services = []
        for row in results:
            service = self.db.get(Service, row[0])
            services.append(TopServiceResponse(
                service_id=row[0],
                service_name=service.name if service else "Unknown",
                booking_count=row[1],
                revenue=float(row[2]),
            ))
        return services

    def _top_technicians(self, limit: int = 5) -> list[TopTechnicianResponse]:
        """Get top technicians by rating and booking count."""
        stmt = (
            select(Technician)
            .order_by(Technician.rating.desc(), Technician.reviews_count.desc())
            .limit(limit)
        )
        technicians = self.db.execute(stmt).scalars().all()
        result = []
        for tech in technicians:
            booking_count = self.db.scalar(
                select(func.count(Booking.id)).where(
                    Booking.technician_id == tech.id,
                    Booking.status == BookingStatus.COMPLETED,
                )
            ) or 0
            revenue = float(
                self.db.scalar(
                    select(func.coalesce(func.sum(Payment.amount), 0))
                    .join(Booking, Payment.booking_id == Booking.id)
                    .where(
                        Booking.technician_id == tech.id,
                        Payment.status == PayStatus.PAID,
                    )
                ) or 0.0
            )
            result.append(TopTechnicianResponse(
                technician_id=tech.id,
                technician_name=tech.user.full_name if tech.user else "Unknown",
                booking_count=booking_count,
                revenue=revenue,
                rating=tech.rating,
            ))
        return result

    def _recent_bookings(self, limit: int = 10) -> list[RecentBookingResponse]:
        """Get the most recent bookings."""
        stmt = (
            select(Booking)
            .order_by(Booking.created_at.desc())
            .limit(limit)
        )
        bookings = self.db.execute(stmt).scalars().all()
        result = []
        for booking in bookings:
            customer_name = booking.customer.user.full_name if booking.customer and booking.customer.user else "N/A"
            service_name = booking.service.name if booking.service else "N/A"
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

