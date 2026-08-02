from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Date,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.bookings import Booking
    from app.models.auth import User


class Coupon(Base):
    """
    Represents a discount coupon/promo code that can be applied to bookings.
    """
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    discount_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="percentage",  # "percentage" | "fixed"
    )

    discount_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    min_order_value: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        default=0.0,
    )

    max_discount: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Maximum discount amount for percentage coupons",
    )

    usage_limit: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Total number of times this coupon can be used",
    )

    usage_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    per_user_limit: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Maximum times a single user can use this coupon",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    valid_from: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    valid_until: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    applicable_services: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="JSON list of service IDs this coupon applies to (null = all)",
    )

    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by],
    )

    usages: Mapped[list["CouponUsage"]] = relationship(
        "CouponUsage",
        back_populates="coupon",
        cascade="all, delete-orphan",
    )


class CouponUsage(Base):
    """
    Tracks usage of coupons per user and per booking.
    """
    __tablename__ = "coupon_usages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    coupon_id: Mapped[int] = mapped_column(
        ForeignKey("coupons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    booking_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("bookings.id", ondelete="SET NULL"),
        nullable=True,
    )

    discount_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    coupon: Mapped["Coupon"] = relationship(
        "Coupon",
        back_populates="usages",
    )

    user: Mapped["User"] = relationship("User")

    booking: Mapped[Optional["Booking"]] = relationship("Booking")

