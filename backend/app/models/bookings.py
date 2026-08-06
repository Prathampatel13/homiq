from __future__ import annotations

from datetime import date, datetime, time, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Date,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.users import Customer, Technician
    from app.models.addresses import CustomerAddress
    from app.models.services import Service
    from app.models.payments import Payment
    from app.models.invoices import Invoice


class BookingStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    ON_THE_WAY = "on_the_way"
    ARRIVED = "arrived"
    WAITING_QR = "waiting_qr"
    QR_VERIFIED = "qr_verified"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    WAITING_PAYMENT = "waiting_payment"
    PAID = "paid"
    REVIEW_PENDING = "review_pending"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REJECTED = "rejected"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    booking_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    technician_id: Mapped[object] = mapped_column(
        ForeignKey("technicians.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )

    address_id: Mapped[int] = mapped_column(
        ForeignKey("customer_addresses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    booking_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    preferred_time: Mapped[object] = mapped_column(
        Time,
        nullable=True,
    )

    estimated_price: Mapped[object] = mapped_column(
        Float,
        nullable=True,
    )

    final_price: Mapped[object] = mapped_column(
        Float,
        nullable=True,
    )

    status: Mapped[BookingStatus] = mapped_column(
        SAEnum(BookingStatus, native_enum=False),
        default=BookingStatus.PENDING,
        nullable=False,
    )

    payment_status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus, native_enum=False),
        default=PaymentStatus.PENDING,
        nullable=False,
    )

    customer_note: Mapped[object] = mapped_column(
        Text,
        nullable=True,
    )

    admin_note: Mapped[object] = mapped_column(
        Text,
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

    # -----------------------------
    # Relationships
    # -----------------------------

    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="bookings",
    )

    technician: Mapped[object] = relationship(
        "Technician",
        back_populates="bookings",
    )

    service: Mapped["Service"] = relationship(
        "Service",
        back_populates="bookings",
    )

    address: Mapped["CustomerAddress"] = relationship(
        "CustomerAddress",
        back_populates="bookings",
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="booking",
        cascade="all, delete-orphan",
    )

    invoices: Mapped[list["Invoice"]] = relationship(
        "Invoice",
        back_populates="booking",
        cascade="all, delete-orphan",
    )

    status_logs: Mapped[list["BookingStatusLog"]] = relationship(
        "BookingStatusLog",
        back_populates="booking",
        cascade="all, delete-orphan",
    )


class BookingStatusLog(Base):
    """Audit trail for every booking status change.

    Records the old and new status, the user who performed the change,
    an optional reason, and the timestamp.  This is the single source of
    truth for the booking lifecycle history.
    """

    __tablename__ = "booking_status_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    old_status: Mapped[Optional[BookingStatus]] = mapped_column(
        SAEnum(BookingStatus, native_enum=False),
        nullable=True,
    )

    new_status: Mapped[BookingStatus] = mapped_column(
        SAEnum(BookingStatus, native_enum=False),
        nullable=False,
    )

    changed_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    booking: Mapped["Booking"] = relationship(
        "Booking",
        back_populates="status_logs",
    )
