from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.auth import User
from app.models.users import Customer, Technician
from app.models.bookings import Booking, BookingStatus, PaymentStatus as BookingPayStatus
from app.models.payments import Payment, PaymentStatus as PayStatus
from app.models.coupons import CouponUsage
from app.models.reviews import Review
from app.models.services import Service


class AnalyticsCRUD:
    """Data aggregation CRUD for Reports & Analytics."""

    def __init__(self, db: Session):
        self.db = db

    def get_user_counts(self) -> dict[str, int]:
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        total_users = self.db.scalar(select(func.count(User.id))) or 0
        new_users = self.db.scalar(select(func.count(User.id)).where(User.created_at >= thirty_days_ago)) or 0
        active_users = self.db.scalar(select(func.count(User.id)).where(User.is_active.is_(True))) or 0
        inactive_users = self.db.scalar(select(func.count(User.id)).where(User.is_active.is_(False))) or 0

        return {
            "total_users": total_users,
            "new_users": new_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
        }

    def get_technician_counts(self) -> dict[str, int]:
        total_technicians = self.db.scalar(select(func.count(Technician.id))) or 0
        verified = self.db.scalar(select(func.count(Technician.id)).where(Technician.government_id_image.isnot(None))) or 0
        pending = total_technicians - verified
        online = self.db.scalar(select(func.count(Technician.id)).where(Technician.is_online.is_(True))) or 0
        offline = total_technicians - online

        return {
            "total_technicians": total_technicians,
            "verified_technicians": verified,
            "pending_verification": pending,
            "online_technicians": online,
            "offline_technicians": offline,
        }

    def get_booking_timeframe_counts(self) -> dict[str, int]:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start.replace(day=1)

        todays = self.db.scalar(select(func.count(Booking.id)).where(Booking.created_at >= today_start)) or 0
        weekly = self.db.scalar(select(func.count(Booking.id)).where(Booking.created_at >= week_start)) or 0
        monthly = self.db.scalar(select(func.count(Booking.id)).where(Booking.created_at >= month_start)) or 0
        cancelled = self.db.scalar(select(func.count(Booking.id)).where(Booking.status == BookingStatus.CANCELLED)) or 0
        completed = self.db.scalar(
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
        pending = self.db.scalar(select(func.count(Booking.id)).where(Booking.status == BookingStatus.PENDING)) or 0

        return {
            "todays_bookings": todays,
            "weekly_bookings": weekly,
            "monthly_bookings": monthly,
            "cancelled_bookings": cancelled,
            "completed_bookings": completed,
            "pending_bookings": pending,
        }

    def get_financial_metrics(self) -> dict[str, float | int]:
        total_rev = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == PayStatus.PAID)
            ) or 0.0
        )
        total_refunds = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == PayStatus.REFUNDED)
            ) or 0.0
        )
        coupons_count = self.db.scalar(select(func.count(CouponUsage.id))) or 0
        avg_rating = float(self.db.scalar(select(func.coalesce(func.avg(Review.rating), 0))) or 0.0)

        return {
            "revenue": round(total_rev, 2),
            "refunds": round(total_refunds, 2),
            "coupons_used": coupons_count,
            "average_rating": round(avg_rating, 2),
        }

    def get_customer_personal_metrics(self, customer_id: int) -> dict[str, Any]:
        total_b = self.db.scalar(select(func.count(Booking.id)).where(Booking.customer_id == customer_id)) or 0
        completed = self.db.scalar(
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
        cancelled = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.customer_id == customer_id,
                Booking.status == BookingStatus.CANCELLED,
            )
        ) or 0
        total_spent = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.customer_id == customer_id,
                    Payment.status == PayStatus.PAID,
                )
            ) or 0.0
        )
        reviews_c = self.db.scalar(select(func.count(Review.id)).where(Review.customer_id == customer_id)) or 0

        # Favourite services
        fav_stmt = text("""
            SELECT s.name, COUNT(b.id) as count
            FROM bookings b
            JOIN services s ON b.service_id = s.id
            WHERE b.customer_id = :cid
            GROUP BY s.name
            ORDER BY count DESC
            LIMIT 5
        """)
        fav_results = self.db.execute(fav_stmt, {"cid": customer_id}).all()
        fav_services = [{"service_name": row[0], "count": row[1]} for row in fav_results]

        return {
            "total_bookings": total_b,
            "completed_jobs": completed,
            "cancelled_jobs": cancelled,
            "total_spent": round(total_spent, 2),
            "favourite_services": fav_services,
            "reviews_count": reviews_c,
        }

    def get_technician_personal_metrics(self, technician_id: int) -> dict[str, Any]:
        completed = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.technician_id == technician_id,
                Booking.status.in_([
                    BookingStatus.COMPLETED,
                    BookingStatus.WAITING_PAYMENT,
                    BookingStatus.PAID,
                    BookingStatus.REVIEW_PENDING,
                    BookingStatus.CLOSED,
                ]),
            )
        ) or 0
        pending = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.technician_id == technician_id,
                Booking.status.in_([BookingStatus.ASSIGNED, BookingStatus.ACCEPTED, BookingStatus.IN_PROGRESS]),
            )
        ) or 0
        cancelled = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.technician_id == technician_id,
                Booking.status.in_([BookingStatus.CANCELLED, BookingStatus.REJECTED]),
            )
        ) or 0

        total_assigned = completed + pending + cancelled
        acceptance_rate = round((completed / total_assigned) * 100.0, 1) if total_assigned > 0 else 100.0
        cancellation_rate = round((cancelled / total_assigned) * 100.0, 1) if total_assigned > 0 else 0.0

        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_earnings = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Booking.final_price), 0)).where(
                    Booking.technician_id == technician_id,
                    Booking.status.in_([BookingStatus.COMPLETED, BookingStatus.PAID]),
                    Booking.updated_at >= month_start,
                )
            ) or 0.0
        )

        avg_r = float(self.db.scalar(select(func.coalesce(func.avg(Review.rating), 0)).where(Review.technician_id == technician_id)) or 0.0)

        tech = self.db.get(Technician, technician_id)
        working_hours = tech.working_hours if (tech and tech.working_hours) else "9:00 AM - 6:00 PM"

        return {
            "completed_jobs": completed,
            "pending_jobs": pending,
            "monthly_earnings": round(monthly_earnings, 2),
            "average_rating": round(avg_r, 2),
            "acceptance_rate": acceptance_rate,
            "cancellation_rate": cancellation_rate,
            "working_hours": working_hours,
        }
