from datetime import date, time, datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Enum as SAEnum, Float, ForeignKey, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.users import Customer, Technician
    from app.models.addresses import CustomerAddress
    from app.models.services import Service


class BookingStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    booking_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    technician_id: Mapped[Optional[int]] = mapped_column(ForeignKey("technicians.id", ondelete="SET NULL"), nullable=True, index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="SET NULL"), nullable=False, index=True)
    address_id: Mapped[int] = mapped_column(ForeignKey("customer_addresses.id", ondelete="CASCADE"), nullable=False, index=True)

    booking_date: Mapped[date] = mapped_column(Date, nullable=False)
    preferred_time: Mapped[Optional[time]] = mapped_column(Time(timezone=False), nullable=True)

    estimated_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    final_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

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

    customer_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    admin_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    customer: Mapped["Customer"] = relationship(
        "Customer",
        foreign_keys=[customer_id],
        backref="bookings",
        lazy="select",
    )

    technician: Mapped[Optional["Technician"]] = relationship(
        "Technician",
        foreign_keys=[technician_id],
        backref="bookings",
        lazy="select",
    )

    service: Mapped["Service"] = relationship(
        "Service",
        foreign_keys=[service_id],
        backref="bookings",
        lazy="select",
    )

    address: Mapped["CustomerAddress"] = relationship(
        "CustomerAddress",
        foreign_keys=[address_id],
        backref="bookings",
        lazy="select",
    )
