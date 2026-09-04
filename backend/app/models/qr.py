from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class QRVerification(Base):
    __tablename__ = "qr_verifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), nullable=False)
    technician_id: Mapped[int] = mapped_column(ForeignKey("technicians.id"), nullable=False)
    
    # QR Token fields (Technician displays, Customer scans)
    token: Mapped[str] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # PIN fields (Backend generates, Customer provides, Technician enters)
    customer_pin_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pin_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    pin_attempt_count: Mapped[int] = mapped_column(default=0, server_default="0", nullable=False)
    
    # Verification Timestamps
    customer_pin_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    technician_qr_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    customer_confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    technician_confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Overall Status
    verification_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    
    # Legacy fields
    verification_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    device_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
