from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.bookings import Booking
    from app.models.payments import Payment
    from app.models.users import Customer


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Invoice(Base):
    """
    Represents an invoice generated for a completed booking or service.
    """
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    invoice_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

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

    payment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("payments.id", ondelete="SET NULL"),
        nullable=True,
    )

    subtotal: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Total before tax and discount",
    )

    discount_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    coupon_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    tax_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    tax_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    total_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Final amount after tax and discount",
    )

    amount_paid: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    amount_due: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    status: Mapped[InvoiceStatus] = mapped_column(
        SAEnum(InvoiceStatus, native_enum=False),
        default=InvoiceStatus.DRAFT,
        nullable=False,
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    issued_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    due_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
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
    booking: Mapped["Booking"] = relationship(
        "Booking",
        back_populates="invoices",
    )

    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="invoices",
    )

    payment: Mapped[Optional["Payment"]] = relationship(
        "Payment",
        foreign_keys=[payment_id],
    )

