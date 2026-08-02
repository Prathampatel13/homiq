from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.bookings import Booking
    from app.models.users import Customer


class PaymentStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CARD = "card"
    UPI = "upi"
    NETBANKING = "netbanking"
    WALLET = "wallet"
    EMI = "emi"
    UNKNOWN = "unknown"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="INR",
        nullable=False,
    )

    razorpay_order_id: Mapped[object] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    razorpay_payment_id: Mapped[object] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    razorpay_signature: Mapped[object] = mapped_column(
        String(500),
        nullable=True,
    )

    payment_method: Mapped[PaymentMethod] = mapped_column(
        SAEnum(PaymentMethod, native_enum=False),
        default=PaymentMethod.UNKNOWN,
        nullable=False,
    )

    status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus, native_enum=False),
        default=PaymentStatus.CREATED,
        nullable=False,
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

    # -----------------------------
    # Relationships
    # -----------------------------

    booking: Mapped["Booking"] = relationship(
        "Booking",
        back_populates="payments",
    )

    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="payments",
    )