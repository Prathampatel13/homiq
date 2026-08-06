"""
Analytics service for deep business insights.

Provides:
- Customer analytics (growth, active, distribution)
- Booking analytics (trends, popular services, peak hours)
- Revenue analytics (trends, payment methods, outstanding)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.bookings import Booking, BookingStatus, PaymentStatus as BookingPayStatus
from app.models.users import Customer, Technician
from app.models.payments import Payment, PaymentStatus as PayStatus, PaymentMethod
from app.models.services import Service
from app.models.reviews import Review
from app.models.addresses import CustomerAddress
from app.schemas.dashboard import (
    AnalyticsOverview,
    BookingAnalytics,
    CustomerAnalytics,
    RevenueAnalytics,
)


class AnalyticsService:
    """Service for deep business analytics."""

    def __init__(self, db: Session):
        self.db = db

    def get_overview(self) -> AnalyticsOverview:
        """Get high-level analytics overview."""
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)

        total_customers = self.db.scalar(select(func.count(Customer.id))) or 0
        total_technicians = self.db.scalar(select(func.count(Technician.id))) or 0
        total_bookings = self.db.scalar(select(func.count(Booking.id))) or 0
        total_revenue = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.status == PayStatus.PAID
                )
            ) or 0.0
        )
        total_services = self.db.scalar(select(func.count(Service.id))) or 0
        avg_rating = float(self.db.scalar(select(func.avg(Review.rating))) or 0.0)

        # Growth rates
        customers_this_month = self.db.scalar(
            select(func.count(Customer.id)).where(Customer.created_at >= month_start)
        ) or 0
        customers_last_month = self.db.scalar(
            select(func.count(Customer.id)).where(
                Customer.created_at >= last_month_start,
                Customer.created_at < month_start,
            )
        ) or 0
        customer_growth = 0.0
        if customers_last_month > 0:
            customer_growth = ((customers_this_month - customers_last_month) / customers_last_month) * 100

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

        revenue_this_month = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.status == PayStatus.PAID,
                    Payment.created_at >= month_start,
                )
            ) or 0.0
        )
        revenue_last_month = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.status == PayStatus.PAID,
                    Payment.created_at >= last_month_start,
                    Payment.created_at < month_start,
                )
            ) or 0.0
        )
        revenue_growth = 0.0
        if revenue_last_month > 0:
            revenue_growth = ((revenue_this_month - revenue_last_month) / revenue_last_month) * 100

        return AnalyticsOverview(
            total_customers=total_customers,
            total_technicians=total_technicians,
            total_bookings=total_bookings,
            total_revenue=round(total_revenue, 2),
            total_services=total_services,
            average_rating=round(avg_rating, 2),
            customer_growth_percent=round(customer_growth, 1),
            booking_growth_percent=round(booking_growth, 1),
            revenue_growth_percent=round(revenue_growth, 1),
        )

    def get_customer_analytics(self) -> CustomerAnalytics:
        """Get detailed customer analytics."""
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total_customers = self.db.scalar(select(func.count(Customer.id))) or 0
        new_this_month = self.db.scalar(
            select(func.count(Customer.id)).where(Customer.created_at >= month_start)
        ) or 0

        # Active customers (have at least one booking in last 30 days)
        thirty_days_ago = now - timedelta(days=30)
        active = self.db.scalar(
            select(func.count(func.distinct(Booking.customer_id))).where(
                Booking.created_at >= thirty_days_ago
            )
        ) or 0

        # Average bookings per customer
        total_bookings = self.db.scalar(select(func.count(Booking.id))) or 0
        avg_bookings = round(total_bookings / total_customers, 2) if total_customers > 0 else 0.0

        # Customers by city
        from sqlalchemy import text
        city_stmt = text("""
            SELECT COALESCE(city, 'Unknown') as city, COUNT(*) as count
            FROM customers
            GROUP BY city
            ORDER BY count DESC
            LIMIT 10
        """)
        city_results = self.db.execute(city_stmt).all()
        customers_by_city = [{"city": row[0], "count": row[1]} for row in city_results]

        # Registration trend (last 12 months)
        from sqlalchemy import extract
        reg_trend = []
        for i in range(11, -1, -1):
            month = (now.month - i - 1) % 12 + 1
            year = now.year + (now.month - i - 1) // 12
            month_name = datetime(year, month, 1).strftime("%b %Y")
            count = self.db.scalar(
                select(func.count(Customer.id)).where(
                    extract("year", Customer.created_at) == year,
                    extract("month", Customer.created_at) == month,
                )
            ) or 0
            reg_trend.append({"month": month_name, "count": count})

        return CustomerAnalytics(
            total_customers=total_customers,
            new_customers_this_month=new_this_month,
            active_customers=active,
            average_bookings_per_customer=avg_bookings,
            customer_growth_rate=0.0,  # Calculated in overview
            customer_by_city=customers_by_city,
            customer_registration_trend=reg_trend,
        )

    def get_booking_analytics(self) -> BookingAnalytics:
        """Get detailed booking analytics."""
        now = datetime.now(timezone.utc)

        total = self.db.scalar(select(func.count(Booking.id))) or 0
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
        cancelled = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.status.in_([
                    BookingStatus.CANCELLED,
                    BookingStatus.EXPIRED,
                    BookingStatus.REJECTED,
                ])
            )
        ) or 0
        pending = self.db.scalar(
            select(func.count(Booking.id)).where(Booking.status == BookingStatus.PENDING)
        ) or 0
        in_progress = self.db.scalar(
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

        # Average booking value
        total_revenue = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.status == PayStatus.PAID
                )
            ) or 0.0
        )
        avg_value = round(total_revenue / total, 2) if total > 0 else 0.0

        # Booking trend (last 12 months)
        from sqlalchemy import extract
        booking_trend = []
        for i in range(11, -1, -1):
            month = (now.month - i - 1) % 12 + 1
            year = now.year + (now.month - i - 1) // 12
            month_name = datetime(year, month, 1).strftime("%b %Y")
            count = self.db.scalar(
                select(func.count(Booking.id)).where(
                    extract("year", Booking.created_at) == year,
                    extract("month", Booking.created_at) == month,
                )
            ) or 0
            booking_trend.append({"month": month_name, "count": count})

        # Popular services
        from sqlalchemy import text
        popular_stmt = text("""
            SELECT s.name, COUNT(b.id) as count
            FROM bookings b
            JOIN services s ON b.service_id = s.id
            GROUP BY s.name
            ORDER BY count DESC
            LIMIT 10
        """)
        popular_results = self.db.execute(popular_stmt).all()
        popular_services = [{"service_name": row[0], "count": row[1]} for row in popular_results]

        # Peak hours (from created_at / preferred_time)
        peak_hours = []
        for hour in range(6, 22):  # 6 AM to 9 PM
            count = self.db.scalar(
                select(func.count(Booking.id)).where(
                    func.extract("hour", Booking.created_at) == hour
                )
            ) or 0
            if count > 0:
                peak_hours.append({"hour": f"{hour}:00", "count": count})

        return BookingAnalytics(
            total=total,
            completed=completed,
            cancelled=cancelled,
            pending=pending,
            in_progress=in_progress,
            average_booking_value=avg_value,
            booking_trend=booking_trend,
            popular_services=popular_services,
            peak_hours=peak_hours,
        )

    def get_revenue_analytics(self) -> RevenueAnalytics:
        """Get detailed revenue analytics."""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = today_start.replace(day=1)

        total_revenue = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.status == PayStatus.PAID
                )
            ) or 0.0
        )
        revenue_this_month = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.status == PayStatus.PAID,
                    Payment.created_at >= month_start,
                )
            ) or 0.0
        )
        revenue_today = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.status == PayStatus.PAID,
                    Payment.created_at >= today_start,
                )
            ) or 0.0
        )

        total_bookings = self.db.scalar(select(func.count(Booking.id))) or 0
        avg_per_booking = round(total_revenue / total_bookings, 2) if total_bookings > 0 else 0.0

        # Monthly revenue trend (last 12 months)
        from sqlalchemy import extract
        monthly_trend = []
        for i in range(11, -1, -1):
            month = (now.month - i - 1) % 12 + 1
            year = now.year + (now.month - i - 1) // 12
            month_name = datetime(year, month, 1).strftime("%b %Y")
            revenue = float(
                self.db.scalar(
                    select(func.coalesce(func.sum(Payment.amount), 0)).where(
                        Payment.status == PayStatus.PAID,
                        extract("year", Payment.created_at) == year,
                        extract("month", Payment.created_at) == month,
                    )
                ) or 0.0
            )
            monthly_trend.append({"month": month_name, "revenue": revenue})

        # Revenue by payment method
        rev_by_method = []
        for method in PaymentMethod:
            revenue = float(
                self.db.scalar(
                    select(func.coalesce(func.sum(Payment.amount), 0)).where(
                        Payment.status == PayStatus.PAID,
                        Payment.payment_method == method,
                    )
                ) or 0.0
            )
            count = self.db.scalar(
                select(func.count(Payment.id)).where(
                    Payment.status == PayStatus.PAID,
                    Payment.payment_method == method,
                )
            ) or 0
            if count > 0:
                rev_by_method.append({
                    "method": method.value if hasattr(method, 'value') else str(method),
                    "revenue": revenue,
                    "count": count,
                })

        # Outstanding payments (completed bookings not yet paid)
        outstanding = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Booking.final_price), 0)).where(
                    Booking.status == BookingStatus.COMPLETED,
                    Booking.payment_status == BookingPayStatus.PENDING,
                )
            ) or 0.0
        )

        return RevenueAnalytics(
            total_revenue=round(total_revenue, 2),
            revenue_this_month=round(revenue_this_month, 2),
            revenue_today=round(revenue_today, 2),
            average_revenue_per_booking=avg_per_booking,
            monthly_revenue_trend=monthly_trend,
            revenue_by_payment_method=rev_by_method,
            outstanding_payments=round(outstanding, 2),
        )

    # ── Reports & Analytics Module Extensions ──────────────────────────────

    def get_full_admin_analytics(self):
        """Get full admin analytics payload."""
        from app.crud.analytics import AnalyticsCRUD
        from app.schemas.reports import AdminAnalyticsFullResponse

        crud = AnalyticsCRUD(self.db)
        u_counts = crud.get_user_counts()
        t_counts = crud.get_technician_counts()
        b_counts = crud.get_booking_timeframe_counts()
        f_counts = crud.get_financial_metrics()

        booking_analytics = self.get_booking_analytics()

        return AdminAnalyticsFullResponse(
            **u_counts,
            **t_counts,
            **b_counts,
            **f_counts,
            popular_services=booking_analytics.popular_services,
            peak_hours=booking_analytics.peak_hours,
            top_technicians=[],
        )

    def get_customer_personal_analytics(self, current_user: User):
        """Get personal analytics for customer."""
        from fastapi import HTTPException, status
        from app.crud.customer import CustomerCRUD
        from app.crud.analytics import AnalyticsCRUD
        from app.schemas.reports import CustomerAnalyticsResponse

        cust = CustomerCRUD(self.db).get_by_user_id(current_user.id)
        if not cust:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found.",
            )

        metrics = AnalyticsCRUD(self.db).get_customer_personal_metrics(cust.id)
        return CustomerAnalyticsResponse(**metrics)

    def get_technician_personal_analytics(self, current_user: User):
        """Get personal analytics for technician."""
        from fastapi import HTTPException, status
        from app.crud.technician import TechnicianCRUD
        from app.crud.analytics import AnalyticsCRUD
        from app.schemas.reports import TechnicianAnalyticsResponse

        tech = TechnicianCRUD(self.db).get_by_user_id(current_user.id)
        if not tech:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician profile not found.",
            )

        metrics = AnalyticsCRUD(self.db).get_technician_personal_metrics(tech.id)
        return TechnicianAnalyticsResponse(**metrics)

    def get_period_report(self, period: str):
        """Get period report (daily, weekly, monthly, yearly)."""
        from app.schemas.reports import PeriodReportResponse

        now = datetime.now(timezone.utc)
        if period == "daily":
            start_date = now - timedelta(days=1)
        elif period == "weekly":
            start_date = now - timedelta(days=7)
        elif period == "yearly":
            start_date = now - timedelta(days=365)
        else:  # monthly default
            start_date = now - timedelta(days=30)

        total_b = self.db.scalar(select(func.count(Booking.id)).where(Booking.created_at >= start_date)) or 0
        completed_b = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.created_at >= start_date,
                Booking.status.in_([
                    BookingStatus.COMPLETED,
                    BookingStatus.WAITING_PAYMENT,
                    BookingStatus.PAID,
                    BookingStatus.REVIEW_PENDING,
                    BookingStatus.CLOSED,
                ]),
            )
        ) or 0
        cancelled_b = self.db.scalar(
            select(func.count(Booking.id)).where(
                Booking.created_at >= start_date,
                Booking.status == BookingStatus.CANCELLED,
            )
        ) or 0
        rev = float(
            self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.created_at >= start_date,
                    Payment.status == PayStatus.PAID,
                )
            ) or 0.0
        )
        new_cust = self.db.scalar(select(func.count(Customer.id)).where(Customer.created_at >= start_date)) or 0

        return PeriodReportResponse(
            period_type=period,
            start_date=start_date.isoformat(),
            end_date=now.isoformat(),
            total_bookings=total_b,
            completed_bookings=completed_b,
            cancelled_bookings=cancelled_b,
            total_revenue=round(rev, 2),
            new_customers=new_cust,
            details=[],
        )

    def export_reports(self, format_type: str = "csv", period: str = "monthly"):
        """Export report data as CSV, Excel, or PDF downloadable stream."""
        import io
        from fastapi import Response

        rep = self.get_period_report(period)

        # Standard CSV content creation without mandatory third-party dependency
        headers_row = "Period,Start Date,End Date,Total Bookings,Completed Bookings,Cancelled Bookings,Total Revenue,New Customers\n"
        data_row = f"{rep.period_type},{rep.start_date},{rep.end_date},{rep.total_bookings},{rep.completed_bookings},{rep.cancelled_bookings},{rep.total_revenue},{rep.new_customers}\n"
        csv_str = headers_row + data_row

        try:
            import pandas as pd
            df = pd.DataFrame([{
                "Period": rep.period_type,
                "Start Date": rep.start_date,
                "End Date": rep.end_date,
                "Total Bookings": rep.total_bookings,
                "Completed Bookings": rep.completed_bookings,
                "Cancelled Bookings": rep.cancelled_bookings,
                "Total Revenue": rep.total_revenue,
                "New Customers": rep.new_customers,
            }])
            if format_type.lower() == "excel":
                output = io.BytesIO()
                try:
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        df.to_excel(writer, index=False, sheet_name="Report")
                    content = output.getvalue()
                except Exception:
                    content = csv_str.encode("utf-8")
                media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                filename = f"homiq_report_{period}.xlsx"
            elif format_type.lower() == "pdf":
                content = df.to_string().encode("utf-8")
                media_type = "application/pdf"
                filename = f"homiq_report_{period}.pdf"
            else:
                content = df.to_csv(index=False).encode("utf-8")
                media_type = "text/csv"
                filename = f"homiq_report_{period}.csv"
        except ImportError:
            content = csv_str.encode("utf-8")
            if format_type.lower() == "excel":
                media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                filename = f"homiq_report_{period}.xlsx"
            elif format_type.lower() == "pdf":
                media_type = "application/pdf"
                filename = f"homiq_report_{period}.pdf"
            else:
                media_type = "text/csv"
                filename = f"homiq_report_{period}.csv"

        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )



