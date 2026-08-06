"""
CRUD operations for QR verification and OTP management.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.qr import QRVerification


class QRVerificationCRUD:
    """CRUD interface for qr_verifications table."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, qr_id: int) -> Optional[QRVerification]:
        """Fetch QR verification record by ID."""
        return self.db.get(QRVerification, qr_id)

    def get_by_booking_id(self, booking_id: int) -> Optional[QRVerification]:
        """Fetch latest QR verification record for a booking."""
        stmt = (
            select(QRVerification)
            .where(QRVerification.booking_id == booking_id)
            .order_by(QRVerification.created_at.desc())
        )
        return self.db.scalars(stmt).first()

    def get_active_by_booking(self, booking_id: int) -> Optional[QRVerification]:
        """Fetch non-expired, unused QR verification record for a booking."""
        now = datetime.now(timezone.utc)
        stmt = (
            select(QRVerification)
            .where(
                QRVerification.booking_id == booking_id,
                QRVerification.used.is_(False),
                QRVerification.expires_at > now,
            )
            .order_by(QRVerification.created_at.desc())
        )
        return self.db.scalars(stmt).first()

    def get_by_token(self, token: str) -> Optional[QRVerification]:
        """Fetch QR verification record by encrypted token."""
        stmt = select(QRVerification).where(QRVerification.token == token)
        return self.db.scalars(stmt).first()

    def create_qr_verification(
        self,
        booking_id: int,
        technician_id: int,
        token: str,
        expires_at: datetime,
        verification_code: str = "",
    ) -> QRVerification:
        """Create a new QR verification token for a booking, deactivating older tokens."""
        existing = self.db.scalars(
            select(QRVerification).where(
                QRVerification.booking_id == booking_id,
                QRVerification.used.is_(False),
            )
        ).all()
        for record in existing:
            record.used = True

        qr_record = QRVerification(
            booking_id=booking_id,
            technician_id=technician_id,
            token=token,
            verification_code=verification_code,
            expires_at=expires_at,
            used=False,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(qr_record)
        self.db.commit()
        self.db.refresh(qr_record)
        return qr_record

    def update_verification_code(
        self,
        qr_id: int,
        code: str,
        expires_at: datetime,
    ) -> Optional[QRVerification]:
        """Update 6-digit OTP code and expiry on existing QR record."""
        record = self.get_by_id(qr_id)
        if not record:
            return None
        record.verification_code = code
        record.expires_at = expires_at
        self.db.commit()
        self.db.refresh(record)
        return record

    def mark_used(self, qr_id: int, device_info: Optional[str] = None) -> Optional[QRVerification]:
        """Mark QR verification record as used."""
        record = self.get_by_id(qr_id)
        if not record:
            return None
        record.used = True
        if device_info:
            record.device_info = device_info
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete_by_booking(self, booking_id: int) -> None:
        """Delete all QR records associated with a booking."""
        records = self.db.scalars(
            select(QRVerification).where(QRVerification.booking_id == booking_id)
        ).all()
        for record in records:
            self.db.delete(record)
        self.db.commit()
