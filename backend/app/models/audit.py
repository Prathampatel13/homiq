from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AuditLog(Base):
    """
    Persistent Security Audit Log database model for recording security-critical events,
    authentication failures, permission checks, administrative actions, and payment events.
    """
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="e.g. LOGIN, LOGOUT, FAILED_LOGIN, PASSWORD_CHANGE, ADMIN_ACTION, BOOKING_STATUS_CHANGE, PAYMENT_EVENT",
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="SUCCESS",
        comment="SUCCESS, FAILURE, DENIED, LOCKED",
    )

    details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="JSON payload of masked event details",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
