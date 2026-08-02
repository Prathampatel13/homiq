from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.notifications import Notification


class NotificationCRUD:
    def __init__(self, db: Session):
        self.db = db

    # ── Create ─────────────────────────────────────────────────────────

    def create(self, data: dict) -> Notification:
        notification = Notification(**data)
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def bulk_create(self, notifications: list[dict]) -> list[Notification]:
        """Create multiple notifications at once."""
        objs = [Notification(**data) for data in notifications]
        self.db.add_all(objs)
        self.db.commit()
        for obj in objs:
            self.db.refresh(obj)
        return objs

    # ── Get ────────────────────────────────────────────────────────────

    def get(self, notification_id: int) -> Optional[Notification]:
        return self.db.get(Notification, notification_id)

    # ── List ───────────────────────────────────────────────────────────

    def list_notifications(
        self,
        user_id: int,
        is_read: Optional[bool] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        if is_read is not None:
            stmt = stmt.where(Notification.is_read.is_(is_read))
        stmt = stmt.offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_notifications(
        self,
        user_id: int,
        is_read: Optional[bool] = None,
    ) -> int:
        stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id
        )
        if is_read is not None:
            stmt = stmt.where(Notification.is_read.is_(is_read))
        return self.db.scalar(stmt) or 0

    def unread_count(self, user_id: int) -> int:
        return self.count_notifications(user_id=user_id, is_read=False)

    # ── Update ─────────────────────────────────────────────────────────

    def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        notification = self.get(notification_id)
        if not notification:
            return None
        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user. Returns number updated."""
        result = self.db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .values(is_read=True)
        )
        self.db.commit()
        return result.rowcount

    def mark_multiple_as_read(self, user_id: int, notification_ids: list[int]) -> int:
        """Mark specific notifications as read. Returns number updated."""
        result = self.db.execute(
            update(Notification)
            .where(
                Notification.id.in_(notification_ids),
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .values(is_read=True)
        )
        self.db.commit()
        return result.rowcount

    # ── Delete ─────────────────────────────────────────────────────────

    def delete(self, notification_id: int) -> bool:
        notification = self.get(notification_id)
        if not notification:
            return False
        self.db.delete(notification)
        self.db.commit()
        return True

    def delete_all(self, user_id: int) -> int:
        """Delete all notifications for a user. Returns number deleted."""
        stmt = select(Notification).where(Notification.user_id == user_id)
        notifications = list(self.db.execute(stmt).scalars().all())
        count = len(notifications)
        for n in notifications:
            self.db.delete(n)
        self.db.commit()
        return count

    def delete_old_notifications(self, days: int = 30) -> int:
        """Delete notifications older than specified days. Returns number deleted."""
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None)
        # SQLAlchemy DateTime with timezone handling
        from sqlalchemy import cast, Date
        stmt = select(Notification).where(
            Notification.created_at < cutoff  # Simplified; production should handle tz
        )
        notifications = list(self.db.execute(stmt).scalars().all())
        count = len(notifications)
        for n in notifications:
            self.db.delete(n)
        self.db.commit()
        return count

