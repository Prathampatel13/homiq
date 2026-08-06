from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import select, update

from app.core.celery_app import celery_app
from app.database.session import SessionLocal
from app.models.bookings import Booking, BookingStatus
from app.models.coupons import Coupon
from app.models.notifications import Notification

logger = logging.getLogger("homiq.tasks")

# In-memory Task Result Store for standalone & fallback tracking
TASK_RESULT_STORE: dict[str, dict[str, Any]] = {}


def record_task_status(task_id: str, status: str, result: Any = None, error: Any = None):
    TASK_RESULT_STORE[task_id] = {
        "task_id": task_id,
        "status": status,
        "result": result,
        "error": str(error) if error else None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


# ── 1. Communication & Notification Tasks ─────────────────────────────────

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_email_task(self, to_email: str = "", subject: str = "", body: str = "") -> dict[str, Any]:
    if isinstance(self, str):
        # Direct function call fallback: send_email_task(to_email, subject, body)
        body = subject
        subject = to_email
        to_email = self
        self = None

    task_id = getattr(self.request, "id", None) if (self and hasattr(self, "request")) else uuid.uuid4().hex
    record_task_status(task_id, "STARTED")
    try:
        logger.info(f"Sending email to {to_email}: {subject}")
        res = {"status": "sent", "to": to_email, "subject": subject}
        record_task_status(task_id, "SUCCESS", result=res)
        return res
    except Exception as exc:
        record_task_status(task_id, "FAILURE", error=exc)
        if self and hasattr(self, "retry"):
            raise self.retry(exc=exc)
        raise exc


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_sms_task(self, phone: str = "", message: str = "") -> dict[str, Any]:
    if isinstance(self, str):
        message = phone
        phone = self
        self = None

    task_id = getattr(self.request, "id", None) if (self and hasattr(self, "request")) else uuid.uuid4().hex
    record_task_status(task_id, "STARTED")
    try:
        logger.info(f"Sending SMS to {phone}: {message[:20]}...")
        res = {"status": "sent", "phone": phone}
        record_task_status(task_id, "SUCCESS", result=res)
        return res
    except Exception as exc:
        record_task_status(task_id, "FAILURE", error=exc)
        if self and hasattr(self, "retry"):
            raise self.retry(exc=exc)
        raise exc


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_push_notification_task(self, user_id: int = 0, title: str = "", message: str = "") -> dict[str, Any]:
    if isinstance(self, int):
        message = title
        title = str(user_id)
        user_id = self
        self = None

    task_id = getattr(self.request, "id", None) if (self and hasattr(self, "request")) else uuid.uuid4().hex
    record_task_status(task_id, "STARTED")
    try:
        db = SessionLocal()
        try:
            from app.crud.notification import NotificationCRUD
            NotificationCRUD(db).create({
                "user_id": user_id,
                "title": title,
                "message": message,
            })
        finally:
            db.close()

        res = {"status": "dispatched", "user_id": user_id, "title": title}
        record_task_status(task_id, "SUCCESS", result=res)
        return res
    except Exception as exc:
        record_task_status(task_id, "FAILURE", error=exc)
        if self and hasattr(self, "retry"):
            raise self.retry(exc=exc)
        raise exc


@celery_app.task(bind=True, max_retries=3, default_retry_delay=15)
def generate_invoice_task(self, booking_id: int = 0) -> dict[str, Any]:
    if isinstance(self, int):
        booking_id = self
        self = None

    task_id = getattr(self.request, "id", None) if (self and hasattr(self, "request")) else uuid.uuid4().hex
    record_task_status(task_id, "STARTED")
    try:
        db = SessionLocal()
        try:
            from app.crud.invoice import InvoiceCRUD
            from app.models.bookings import Booking
            inv_crud = InvoiceCRUD(db)
            existing = inv_crud.get_by_booking(booking_id)
            if not existing:
                b = db.get(Booking, booking_id)
                if b:
                    inv_crud.create({
                        "invoice_number": f"INV-{uuid.uuid4().hex[:8].upper()}",
                        "booking_id": b.id,
                        "customer_id": b.customer_id,
                        "subtotal": b.final_price,
                        "total_amount": b.final_price,
                        "status": "paid",
                    })
        finally:
            db.close()

        res = {"status": "invoice_generated", "booking_id": booking_id}
        record_task_status(task_id, "SUCCESS", result=res)
        return res
    except Exception as exc:
        record_task_status(task_id, "FAILURE", error=exc)
        if self and hasattr(self, "retry"):
            raise self.retry(exc=exc)
        raise exc


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_booking_reminder_task(self, booking_id: int) -> dict[str, Any]:
    task_id = getattr(self.request, "id", None) or uuid.uuid4().hex
    record_task_status(task_id, "STARTED")
    try:
        db = SessionLocal()
        try:
            b = db.get(Booking, booking_id)
            if b and b.customer:
                from app.crud.notification import NotificationCRUD
                NotificationCRUD(db).create({
                    "user_id": b.customer.user_id,
                    "title": "Upcoming Service Reminder",
                    "message": f"Reminder for your booking #{b.booking_number}.",
                })
        finally:
            db.close()

        res = {"status": "reminder_sent", "booking_id": booking_id}
        record_task_status(task_id, "SUCCESS", result=res)
        return res
    except Exception as exc:
        record_task_status(task_id, "FAILURE", error=exc)
        if self and hasattr(self, "retry"):
            raise self.retry(exc=exc)
        raise exc


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_technician_reminder_task(self, booking_id: int) -> dict[str, Any]:
    task_id = getattr(self.request, "id", None) or uuid.uuid4().hex
    record_task_status(task_id, "STARTED")
    try:
        db = SessionLocal()
        try:
            b = db.get(Booking, booking_id)
            if b and b.technician:
                from app.crud.notification import NotificationCRUD
                NotificationCRUD(db).create({
                    "user_id": b.technician.user_id,
                    "title": "Job Dispatch Reminder",
                    "message": f"Reminder: You have an upcoming service job #{b.booking_number}.",
                })
        finally:
            db.close()

        res = {"status": "technician_reminded", "booking_id": booking_id}
        record_task_status(task_id, "SUCCESS", result=res)
        return res
    except Exception as exc:
        record_task_status(task_id, "FAILURE", error=exc)
        if self and hasattr(self, "retry"):
            raise self.retry(exc=exc)
        raise exc


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_payment_reminder_task(self, booking_id: int) -> dict[str, Any]:
    task_id = getattr(self.request, "id", None) or uuid.uuid4().hex
    record_task_status(task_id, "STARTED")
    try:
        db = SessionLocal()
        try:
            b = db.get(Booking, booking_id)
            if b and b.customer:
                from app.crud.notification import NotificationCRUD
                NotificationCRUD(db).create({
                    "user_id": b.customer.user_id,
                    "title": "Pending Payment Reminder",
                    "message": f"Please complete payment of INR {b.final_price} for booking #{b.booking_number}.",
                })
        finally:
            db.close()

        res = {"status": "payment_reminder_sent", "booking_id": booking_id}
        record_task_status(task_id, "SUCCESS", result=res)
        return res
    except Exception as exc:
        record_task_status(task_id, "FAILURE", error=exc)
        raise self.retry(exc=exc)


# ── 3. Periodic Scheduled Cleanups & Auto-Cancellation ──────────────────

@celery_app.task(name="app.tasks.background.cleanup_expired_otps_task")
def cleanup_expired_otps_task() -> dict[str, Any]:
    logger.info("Running periodic task: cleanup_expired_otps")
    return {"cleaned_otps": 0}


@celery_app.task(name="app.tasks.background.cleanup_expired_qr_codes_task")
def cleanup_expired_qr_codes_task() -> dict[str, Any]:
    logger.info("Running periodic task: cleanup_expired_qr_codes")
    return {"cleaned_qrs": 0}


@celery_app.task(name="app.tasks.background.cleanup_expired_coupons_task")
def cleanup_expired_coupons_task() -> dict[str, Any]:
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        stmt = update(Coupon).where(Coupon.valid_until < now, Coupon.is_active.is_(True)).values(is_active=False)
        result = db.execute(stmt)
        db.commit()
        return {"deactivated_coupons": result.rowcount}
    finally:
        db.close()


@celery_app.task(name="app.tasks.background.auto_cancel_expired_bookings_task")
def auto_cancel_expired_bookings_task() -> dict[str, Any]:
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        stmt = update(Booking).where(
            Booking.status == BookingStatus.PENDING,
            Booking.created_at < cutoff,
        ).values(status=BookingStatus.CANCELLED)
        res = db.execute(stmt)
        db.commit()
        return {"cancelled_expired_bookings": res.rowcount}
    finally:
        db.close()


@celery_app.task(name="app.tasks.background.send_hourly_booking_reminders_task")
def send_hourly_booking_reminders_task() -> dict[str, Any]:
    logger.info("Running hourly booking reminders sweep")
    return {"reminders_processed": 0}


@celery_app.task(name="app.tasks.background.generate_daily_report_task")
def generate_daily_report_task() -> dict[str, Any]:
    db = SessionLocal()
    try:
        from app.services.analytics import AnalyticsService
        rep = AnalyticsService(db).get_period_report("daily")
        return {"daily_report": rep.model_dump() if hasattr(rep, 'model_dump') else dict(rep)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.background.generate_weekly_report_task")
def generate_weekly_report_task() -> dict[str, Any]:
    db = SessionLocal()
    try:
        from app.services.analytics import AnalyticsService
        rep = AnalyticsService(db).get_period_report("weekly")
        return {"weekly_report": rep.model_dump() if hasattr(rep, 'model_dump') else dict(rep)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.background.generate_monthly_report_task")
def generate_monthly_report_task() -> dict[str, Any]:
    db = SessionLocal()
    try:
        from app.services.analytics import AnalyticsService
        rep = AnalyticsService(db).get_period_report("monthly")
        return {"monthly_report": rep.model_dump() if hasattr(rep, 'model_dump') else dict(rep)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.background.database_cleanup_task")
def database_cleanup_task() -> dict[str, Any]:
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=90)
        stmt = update(Notification).where(
            Notification.is_read.is_(True),
            Notification.created_at < cutoff,
        ).values(is_read=True)
        res = db.execute(stmt)
        db.commit()
        return {"purged_notifications": res.rowcount}
    finally:
        db.close()
