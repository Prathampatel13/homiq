"""
Notification management endpoints.

All authenticated users can:
- List their notifications
- Mark notifications as read
- Delete notifications
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user
from app.schemas.notifications import (
    MultiChannelNotificationCreate,
    NotificationCreate,
    NotificationDispatchResult,
    NotificationListResponse,
    NotificationMarkRead,
    NotificationResponse,
    UnreadNotificationsResponse,
)
from app.services.notification import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "/",
    response_model=NotificationListResponse,
    summary="List user notifications",
    description="Returns a paginated list of notifications for the authenticated user. Includes unread count.",
)
def list_notifications(
    is_read: Optional[bool] = None,
    offset: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """List notifications for the current user."""
    return NotificationService(db).list_notifications(
        current_user,
        is_read=is_read,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/unread",
    response_model=UnreadNotificationsResponse,
    summary="Get unread notifications",
    description="Returns all unread notifications and the unread count for the authenticated user.",
)
def get_unread_notifications(
    offset: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get unread notifications for current user."""
    return NotificationService(db).get_unread_notifications(current_user, offset=offset, limit=limit)


@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a notification (Admin/System)",
    description="**Admin/System use.** Creates a notification for a user. Used for system-generated notifications.",
)
def create_notification(
    payload: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create a notification for a user (admin/system use)."""
    return NotificationService(db).create_notification(payload)


@router.post(
    "/dispatch",
    response_model=NotificationDispatchResult,
    status_code=status.HTTP_200_OK,
    summary="Dispatch multi-channel notification",
    description="Dispatches a notification across Email, SMS, Push, and In-App channels in the background.",
)
def dispatch_notification(
    payload: MultiChannelNotificationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Dispatch multi-channel notification in the background."""
    service = NotificationService(db)
    background_tasks.add_task(service.dispatch_multi_channel_notification, payload)
    return service.dispatch_multi_channel_notification(payload)


# ─── MARK AS READ ENDPOINTS ──────────────────────────────────────────────


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark notification as read (PATCH)",
    description="Marks a single notification as read for the authenticated user.",
)
def patch_mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Mark a notification as read via PATCH."""
    return NotificationService(db).mark_as_read(current_user, notification_id)


@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark notification as read (PUT)",
    description="Marks a single notification as read for the authenticated user.",
)
def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Mark a notification as read via PUT."""
    return NotificationService(db).mark_as_read(current_user, notification_id)


@router.patch(
    "/read-all",
    summary="Mark all notifications as read (PATCH)",
    description="Marks all notifications as read for the authenticated user.",
)
def patch_mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Mark all notifications as read via PATCH."""
    return NotificationService(db).mark_all_as_read(current_user)


@router.put(
    "/read-all",
    summary="Mark all notifications as read (PUT)",
    description="Marks all notifications as read for the authenticated user.",
)
def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Mark all notifications as read via PUT."""
    return NotificationService(db).mark_all_as_read(current_user)


@router.post(
    "/read-multiple",
    summary="Mark multiple notifications as read",
    description="Marks a specific set of notification IDs as read.",
)
def mark_multiple_as_read(
    payload: NotificationMarkRead,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Mark multiple notifications as read."""
    return NotificationService(db).mark_multiple_as_read(current_user, payload)


# ─── DELETE ENDPOINTS ───────────────────────────────────────────────────


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a notification",
    description="Deletes a single notification by its ID. Only the notification owner can delete.",
)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Delete a notification by ID."""
    return NotificationService(db).delete_notification(current_user, notification_id)


@router.delete(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Delete all notifications",
    description="Deletes all notifications for the authenticated user.",
)
def delete_all_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Delete all notifications for the current user."""
    return NotificationService(db).delete_all_notifications(current_user)


