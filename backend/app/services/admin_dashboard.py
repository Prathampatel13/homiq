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

from app.models.auth import User
from app.models.bookings import Booking, BookingStatus
from app.models.payments import Payment, PaymentStatus as PayStatus
from app.models.reviews import Review
from app.models.services import Category, Service
from app.models.users import Customer, Technician
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
        total_users = self.db.scalar(select(func.count(User.id))) or 0
        total_bookings = self.db.scalar(select(func.count(Booking.id))) or 0
        pending_jobs = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.status.in_([
                    BookingStatus.PENDING,
                    BookingStatus.ASSIGNED,
                    BookingStatus.ACCEPTED,
                ])
            )
        ) or 0
        pending_bookings = self.db.scalar(
            select(func.count(Booking.id)).where(Booking.status == BookingStatus.PENDING)
        ) or 0
        active_bookings = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.status.in_([
                    BookingStatus.ASSIGNED,
                    BookingStatus.ACCEPTED,
                    BookingStatus.ON_THE_WAY,
                    BookingStatus.ARRIVED,
                    BookingStatus.WAITING_QR,
                    BookingStatus.QR_VERIFIED,
                    BookingStatus.IN_PROGRESS,
                ])
            )
        ) or 0
        completed_jobs = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.status.in_([
                    BookingStatus.COMPLETED,
                    BookingStatus.WAITING_PAYMENT,
                    BookingStatus.PAID,
                    BookingStatus.REVIEW_PENDING,
                    BookingStatus.CLOSED,
                ])
            )
        ) or 0
        completed_bookings = completed_jobs
        cancelled_bookings = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.status.in_([
                    BookingStatus.CANCELLED,
                    BookingStatus.EXPIRED,
                    BookingStatus.REJECTED,
                ])
            )
        ) or 0
        total_technicians = self.db.scalar(select(func.count(Technician.id))) or 0
        pending_technicians = self.db.scalar(
            select(func.count(Technician.id))
            .join(User, Technician.user_id == User.id)
            .where(User.is_verified.is_(False))
        ) or 0
        verified_technicians = self.db.scalar(
            select(func.count(Technician.id))
            .join(User, Technician.user_id == User.id)
            .where(User.is_verified.is_(True))
        ) or 0
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
            total_users=total_users,
            total_bookings=total_bookings,
            pending_jobs=pending_jobs,
            completed_jobs=completed_jobs,
            pending_bookings=pending_bookings,
            active_bookings=active_bookings,
            completed_bookings=completed_bookings,
            cancelled_bookings=cancelled_bookings,
            total_technicians=total_technicians,
            pending_technicians=pending_technicians,
            verified_technicians=verified_technicians,
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
                    Booking.status.in_([
                        BookingStatus.COMPLETED,
                        BookingStatus.WAITING_PAYMENT,
                        BookingStatus.PAID,
                        BookingStatus.REVIEW_PENDING,
                        BookingStatus.CLOSED,
                    ]),
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


# ═══════════════════════════════════════════════════════════════════════
# ADMIN USER & TECHNICIAN MANAGEMENT SERVICE
# ═══════════════════════════════════════════════════════════════════════


class AdminUserService:
    """Service layer for Admin User & Technician management."""

    def __init__(self, db: Session):
        self.db = db
        from app.crud.user import UserCRUD
        from app.crud.technician import TechnicianCRUD
        self.user_crud = UserCRUD(db)
        self.technician_crud = TechnicianCRUD(db)

    def list_users(
        self,
        query: str | None = None,
        role: str | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> AdminUserListResponse:
        from app.schemas.dashboard import AdminUserListResponse, AdminUserResponse

        users = self.user_crud.list_users(
            query=query, role=role, is_active=is_active, offset=offset, limit=limit
        )
        total = self.user_crud.count_users(query=query, role=role, is_active=is_active)
        items = [
            AdminUserResponse(
                id=u.id,
                email=u.email,
                full_name=u.full_name,
                phone=u.phone,
                role=u.role.name if u.role else "customer",
                is_active=u.is_active,
                is_verified=u.is_verified,
                is_superuser=u.is_superuser,
                created_at=u.created_at,
                updated_at=u.updated_at,
            )
            for u in users
        ]
        return AdminUserListResponse(items=items, total=total)

    def get_user_detail(self, user_id: int) -> AdminUserDetailResponse:
        from fastapi import HTTPException, status
        from app.models.auth import User
        from app.schemas.dashboard import AdminUserDetailResponse, AdminUserResponse, RecentBookingResponse

        user = self.user_crud.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user_resp = AdminUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role.name if user.role else "customer",
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

        total_bookings = 0
        total_spent = 0.0
        recent_bookings = []

        if user.customer:
            total_bookings = len(user.customer.bookings)
            total_spent = float(
                self.db.scalar(
                    select(func.coalesce(func.sum(Payment.amount), 0))
                    .where(Payment.customer_id == user.customer.id, Payment.status == PayStatus.PAID)
                ) or 0.0
            )
            stmt = (
                select(Booking)
                .where(Booking.customer_id == user.customer.id)
                .order_by(Booking.created_at.desc())
                .limit(5)
            )
            for b in self.db.execute(stmt).scalars().all():
                recent_bookings.append(
                    RecentBookingResponse(
                        id=b.id,
                        booking_number=b.booking_number,
                        customer_name=user.full_name,
                        service_name=b.service.name if b.service else "N/A",
                        status=b.status.value if hasattr(b.status, "value") else str(b.status),
                        amount=b.final_price or b.estimated_price or 0.0,
                        created_at=b.created_at,
                    )
                )

        return AdminUserDetailResponse(
            user=user_resp,
            total_bookings=total_bookings,
            total_spent=round(total_spent, 2),
            recent_bookings=recent_bookings,
        )

    def activate_user(self, user_id: int) -> AdminUserResponse:
        from fastapi import HTTPException, status
        from app.schemas.dashboard import AdminUserResponse

        user = self.user_crud.set_active_status(user_id, is_active=True)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return AdminUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role.name if user.role else "customer",
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def suspend_user(self, user_id: int) -> AdminUserResponse:
        from fastapi import HTTPException, status
        from app.schemas.dashboard import AdminUserResponse

        user = self.user_crud.set_active_status(user_id, is_active=False)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return AdminUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role.name if user.role else "customer",
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def delete_user(self, user_id: int) -> dict[str, str]:
        from fastapi import HTTPException, status

        ok = self.user_crud.delete_user(user_id)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return {"detail": f"User {user_id} deleted successfully"}

    def approve_technician(self, technician_id: int) -> AdminUserResponse:
        from fastapi import HTTPException, status
        from app.schemas.dashboard import AdminUserResponse

        tech = self.technician_crud.get_by_technician_id(technician_id)
        if not tech:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician not found",
            )
        user = self.user_crud.set_verified_status(tech.user_id, is_verified=True)
        return AdminUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role.name if user.role else "technician",
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def reject_technician(self, technician_id: int) -> AdminUserResponse:
        from fastapi import HTTPException, status
        from app.schemas.dashboard import AdminUserResponse

        tech = self.technician_crud.get_by_technician_id(technician_id)
        if not tech:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician not found",
            )
        user = self.user_crud.set_verified_status(tech.user_id, is_verified=False)
        return AdminUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role.name if user.role else "technician",
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def activate_technician(self, technician_id: int):
        from fastapi import HTTPException, status
        from app.schemas.technician import TechnicianResponse

        tech = self.technician_crud.get_by_technician_id(technician_id)
        if not tech:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician not found",
            )
        self.technician_crud.update(technician_id, {"availability": True})
        self.db.refresh(tech)
        from app.services.technician import TechnicianService
        return TechnicianService(self.db)._build_response(tech.user, tech)

    def suspend_technician(self, technician_id: int):
        from fastapi import HTTPException, status
        from app.schemas.technician import TechnicianResponse

        tech = self.technician_crud.get_by_technician_id(technician_id)
        if not tech:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician not found",
            )
        self.technician_crud.update(technician_id, {"availability": False, "is_online": False})
        self.db.refresh(tech)
        from app.services.technician import TechnicianService
        return TechnicianService(self.db)._build_response(tech.user, tech)

    def get_technician_documents(self, technician_id: int):
        from fastapi import HTTPException, status
        from app.schemas.dashboard import TechnicianDocumentResponse

        tech = self.technician_crud.get_by_technician_id(technician_id)
        if not tech:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician not found",
            )
        return TechnicianDocumentResponse(
            technician_id=tech.id,
            user_id=tech.user_id,
            full_name=tech.user.full_name if tech.user else "N/A",
            profile_image=tech.profile_image,
            government_id_image=tech.government_id_image,
            is_verified=getattr(tech.user, "is_verified", False),
        )


# ═══════════════════════════════════════════════════════════════════════
# ADMIN SETTINGS SERVICE
# ═══════════════════════════════════════════════════════════════════════


_SETTINGS_STORE = {
    "platform_name": "HomiQ",
    "support_email": "support@homiq.com",
    "support_phone": "+1-800-HOMIQ",
    "commission_percentage": 10.0,
    "tax_percentage": 18.0,
    "working_hours": "08:00 AM - 08:00 PM",
    "max_active_bookings_per_technician": 1,
    "cancellation_window_hours": 2,
}


class AdminSettingsService:
    """Service layer for Admin System Settings."""

    def __init__(self, db: Session):
        self.db = db

    def get_settings(self):
        from app.schemas.dashboard import AdminSettingsResponse
        return AdminSettingsResponse(**_SETTINGS_STORE)

    def update_settings(self, payload):
        from app.schemas.dashboard import AdminSettingsResponse

        data = payload.model_dump(exclude_unset=True)
        _SETTINGS_STORE.update(data)
        return AdminSettingsResponse(**_SETTINGS_STORE)

