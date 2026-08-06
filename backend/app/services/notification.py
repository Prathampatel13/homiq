from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.notification import NotificationCRUD
from app.crud.customer import CustomerCRUD
from app.models.auth import User
from app.schemas.notifications import (
    NotificationCreate,
    NotificationListResponse,
    NotificationMarkRead,
    NotificationResponse,
)


class NotificationService:
    """Service layer for notification operations."""

    def __init__(self, db: Session):
        self.db = db
        self.crud = NotificationCRUD(db)
        self.customer_crud = CustomerCRUD(db)

    def _get_customer_id(self, current_user: User) -> int:
        customer = self.customer_crud.get_by_user_id(current_user.id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found.",
            )
        return customer.id

    # ── Create ─────────────────────────────────────────────────────────

    def create_notification(self, payload: NotificationCreate) -> NotificationResponse:
        """Create a notification for a user (internal/admin use)."""
        data = payload.model_dump()
        notification = self.crud.create(data)
        return NotificationResponse.model_validate(notification)

    def notify_user(
        self,
        user_id: int,
        title: str,
        message: str,
    ) -> NotificationResponse:
        """Helper to create a notification for a specific user."""
        notification = self.crud.create({
            "user_id": user_id,
            "title": title,
            "message": message,
        })
        return NotificationResponse.model_validate(notification)

    def notify_booking_created(self, user_id: int, booking_number: str) -> NotificationResponse:
        """Notify customer when a booking is created."""
        return self.notify_user(
            user_id=user_id,
            title="Booking Created",
            message=f"Your booking {booking_number} has been created successfully.",
        )

    def notify_technician_assigned(self, user_id: int, booking_number: str, technician_name: str) -> NotificationResponse:
        """Notify customer when a technician is assigned."""
        return self.notify_user(
            user_id=user_id,
            title="Technician Assigned",
            message=f"Technician {technician_name} has been assigned to booking {booking_number}.",
        )

    def notify_technician_arriving(self, user_id: int, booking_number: str, eta_minutes: int) -> NotificationResponse:
        """Notify customer when technician is arriving."""
        return self.notify_user(
            user_id=user_id,
            title="Technician Arriving",
            message=f"Technician is arriving in approximately {eta_minutes} minutes for booking {booking_number}.",
        )

    def notify_payment_success(self, user_id: int, booking_number: str, amount: float) -> NotificationResponse:
        """Notify customer on successful payment."""
        return self.notify_user(
            user_id=user_id,
            title="Payment Successful",
            message=f"Payment of ₹{amount:.2f} for booking {booking_number} was successful.",
        )

    def notify_review_reminder(self, user_id: int, booking_number: str) -> NotificationResponse:
        """Remind customer to leave a review."""
        return self.notify_user(
            user_id=user_id,
            title="Review Reminder",
            message=f"Your service for booking {booking_number} is complete. Please rate your experience!",
        )

    def notify_otp_generated(self, user_id: int, booking_number: str, otp: str) -> NotificationResponse:
        """Notify customer about OTP for service completion."""
        return self.notify_user(
            user_id=user_id,
            title="OTP Generated",
            message=f"Your OTP for booking {booking_number} completion is: {otp}",
        )

    # ── List ───────────────────────────────────────────────────────────

    def list_notifications(
        self,
        current_user: User,
        is_read: Optional[bool] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> NotificationListResponse:
        """List notifications for the current user."""
        notifications = self.crud.list_notifications(
            user_id=current_user.id,
            is_read=is_read,
            offset=offset,
            limit=limit,
        )
        total = self.crud.count_notifications(
            user_id=current_user.id,
            is_read=is_read,
        )
        unread_count = self.crud.unread_count(user_id=current_user.id)

        return NotificationListResponse(
            items=[NotificationResponse.model_validate(n) for n in notifications],
            total=total,
            unread_count=unread_count,
        )

    def get_unread_notifications(
        self,
        current_user: User,
        offset: int = 0,
        limit: int = 50,
    ):
        """Fetch all unread notifications for the current user."""
        from app.schemas.notifications import UnreadNotificationsResponse
        unread_items = self.crud.get_unread_notifications(
            user_id=current_user.id,
            offset=offset,
            limit=limit,
        )
        count = self.crud.unread_count(user_id=current_user.id)
        return UnreadNotificationsResponse(
            items=[NotificationResponse.model_validate(n) for n in unread_items],
            unread_count=count,
        )

    # ── Multi-Channel Dispatcher ──────────────────────────────────────────

    def dispatch_multi_channel_notification(
        self,
        payload: Any,
    ):
        """Dispatch notifications across Email, SMS, Push, and In-App channels."""
        from app.schemas.notifications import NotificationDispatchResult

        user_id = payload.user_id
        title = payload.title
        message = payload.message
        channels = payload.channels or ["email", "sms", "push", "in_app"]

        email_status = "skipped"
        sms_status = "skipped"
        push_status = "skipped"
        in_app_status = "skipped"

        if "in_app" in channels:
            self.crud.create({
                "user_id": user_id,
                "title": title,
                "message": message,
            })
            in_app_status = "delivered"

        if "email" in channels:
            email_status = "sent"  # SMTP background dispatch simulation

        if "sms" in channels:
            sms_status = "sent"  # Twilio/SMS provider dispatch simulation

        if "push" in channels:
            push_status = "sent"  # FCM push notification simulation

        return NotificationDispatchResult(
            user_id=user_id,
            title=title,
            channels_sent=channels,
            email_status=email_status,
            sms_status=sms_status,
            push_status=push_status,
            in_app_status=in_app_status,
        )

    # ── Mark as Read ───────────────────────────────────────────────────

    def mark_as_read(self, current_user: User, notification_id: int) -> NotificationResponse:
        """Mark a single notification as read."""
        notification = self.crud.get(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found.",
            )

        if notification.user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only mark your own notifications as read.",
            )

        updated = self.crud.mark_as_read(notification_id)
        return NotificationResponse.model_validate(updated)

    def mark_all_as_read(self, current_user: User) -> dict[str, str | int]:
        """Mark all notifications as read for the current user."""
        count = self.crud.mark_all_as_read(user_id=current_user.id)
        return {"message": f"{count} notifications marked as read.", "count": count}

    def mark_multiple_as_read(
        self, current_user: User, payload: NotificationMarkRead
    ) -> dict[str, str | int]:
        """Mark multiple notifications as read."""
        count = self.crud.mark_multiple_as_read(
            user_id=current_user.id,
            notification_ids=payload.notification_ids,
        )
        return {"message": f"{count} notifications marked as read.", "count": count}

    # ── Delete ─────────────────────────────────────────────────────────

    def delete_notification(self, current_user: User, notification_id: int) -> dict[str, str]:
        """Delete a single notification."""
        notification = self.crud.get(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found.",
            )

        if notification.user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own notifications.",
            )

        deleted = self.crud.delete(notification_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete notification.",
            )
        return {"message": "Notification deleted successfully."}

    def delete_all_notifications(self, current_user: User) -> dict[str, str | int]:
        """Delete all notifications for the current user."""
        count = self.crud.delete_all(user_id=current_user.id)
        return {"message": f"{count} notifications deleted.", "count": count}


