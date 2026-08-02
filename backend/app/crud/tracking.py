from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.tracking import TrackingEvent


class TrackingCRUD:
    def __init__(self, db: Session):
        self.db = db

    # ── Create ─────────────────────────────────────────────────────────

    def create_event(self, data: dict) -> TrackingEvent:
        event = TrackingEvent(**data)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    # ── Get ────────────────────────────────────────────────────────────

    def get_latest_event(self, booking_id: int) -> Optional[TrackingEvent]:
        """Get the most recent tracking event for a booking."""
        stmt = (
            select(TrackingEvent)
            .where(TrackingEvent.booking_id == booking_id)
            .order_by(TrackingEvent.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    def get_latest_technician_event(self, technician_id: int) -> Optional[TrackingEvent]:
        """Get the most recent tracking event for a technician."""
        stmt = (
            select(TrackingEvent)
            .where(TrackingEvent.technician_id == technician_id)
            .order_by(TrackingEvent.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    # ── List ───────────────────────────────────────────────────────────

    def list_events(
        self,
        booking_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[TrackingEvent]:
        stmt = (
            select(TrackingEvent)
            .where(TrackingEvent.booking_id == booking_id)
            .order_by(TrackingEvent.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def count_events(self, booking_id: int) -> int:
        stmt = select(func.count(TrackingEvent.id)).where(
            TrackingEvent.booking_id == booking_id
        )
        return self.db.scalar(stmt) or 0

    # ── Analytics ──────────────────────────────────────────────────────

    def get_technician_location_history(
        self,
        technician_id: int,
        minutes: int = 30,
    ) -> list[TrackingEvent]:
        """Get location history for a technician within the last N minutes."""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        stmt = (
            select(TrackingEvent)
            .where(
                TrackingEvent.technician_id == technician_id,
                TrackingEvent.created_at >= cutoff,
            )
            .order_by(TrackingEvent.created_at.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def delete_old_events(self, days: int = 90) -> int:
        """Delete tracking events older than specified days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = select(TrackingEvent).where(TrackingEvent.created_at < cutoff)
        events = list(self.db.execute(stmt).scalars().all())
        count = len(events)
        for event in events:
            self.db.delete(event)
        self.db.commit()
        return count

