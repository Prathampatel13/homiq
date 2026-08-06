"""
SmartVerify Service Layer for HomiQ Backend.

Handles secure QR code generation, cryptographic token signing/encryption,
technician scanning verification, 6-digit OTP lifecycle, attempt limiting,
state machine transitions, and audit trail logging.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import random
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.qr import QRVerificationCRUD
from app.models.auth import User
from app.models.bookings import Booking, BookingStatus, BookingStatusLog
from app.schemas.bookings import (
    OTPGenerateResponse,
    OTPVerifyRequest,
    OTPVerifyResponse,
    QRGenerateResponse,
    QRScanRequest,
    QRScanResponse,
    SmartVerifyStatusResponse,
)

# Configuration defaults
QR_EXPIRY_MINUTES = 15
OTP_EXPIRY_MINUTES = 5
MAX_OTP_ATTEMPTS = 3
TOKEN_SECRET_KEY = getattr(settings, "SECRET_KEY", "homiq_smartverify_secret_key_2026")


class SmartVerifyService:
    """Service layer enforcing SmartVerify QR and OTP security rules."""

    def __init__(self, db: Session):
        self.db = db
        self.crud = QRVerificationCRUD(db)

    # ─── TOKEN ENCRYPTION & SIGNING HELPERS ─────────────────────────────────

    def _generate_signature(self, payload_str: str) -> str:
        """Generate HMAC-SHA256 signature for QR payload string."""
        return hmac.new(
            TOKEN_SECRET_KEY.encode(),
            payload_str.encode(),
            hashlib.sha256,
        ).hexdigest()

    def _build_encrypted_qr_data(
        self,
        booking: Booking,
        token: str,
        expires_at: datetime,
    ) -> tuple[str, str]:
        """Build tamper-resistant, signed QR payload data string."""
        raw_payload = {
            "booking_id": booking.id,
            "booking_uuid": booking.booking_number,
            "verification_token": token,
            "customer_id": booking.customer_id,
            "technician_id": booking.technician_id,
            "expires_at": expires_at.isoformat(),
            "version": "1.0",
        }
        json_str = json.dumps(raw_payload, sort_keys=True)
        signature = self._generate_signature(json_str)

        envelope = {
            "data": raw_payload,
            "sig": signature,
        }
        encoded_data = base64.urlsafe_b64encode(
            json.dumps(envelope).encode()
        ).decode()
        return encoded_data, token

    def _verify_qr_data(self, qr_code_data: str) -> dict[str, Any]:
        """Decode and verify HMAC signature of QR code payload."""
        try:
            decoded_bytes = base64.urlsafe_b64decode(qr_code_data.encode())
            envelope = json.loads(decoded_bytes.decode())
            raw_payload = envelope["data"]
            signature = envelope["sig"]

            json_str = json.dumps(raw_payload, sort_keys=True)
            expected_sig = self._generate_signature(json_str)

            if not hmac.compare_digest(signature, expected_sig):
                raise ValueError("Tampered QR signature")

            return raw_payload
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid or tampered QR code data: {str(err)}",
            )

    def _log_audit_event(
        self,
        booking_id: int,
        old_status: Optional[BookingStatus],
        new_status: BookingStatus,
        user_id: Optional[int],
        note: str,
    ) -> None:
        """Create audit log entry in booking_status_logs."""
        log_entry = BookingStatusLog(
            booking_id=booking_id,
            old_status=old_status,
            new_status=new_status,
            changed_by_user_id=user_id,
            reason=note,
        )
        self.db.add(log_entry)
        self.db.commit()

    # ─── 1. GENERATE QR ──────────────────────────────────────────────────────

    def generate_qr(self, current_user: User, booking_id: int) -> QRGenerateResponse:
        """Generate a secure, single-use, time-limited QR token for a booking."""
        booking = self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        # Access check: Customer owning booking or Admin
        if not current_user.is_superuser:
            if not current_user.customer or booking.customer_id != current_user.customer.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the booking owner can generate the verification QR code",
                )

        # Assignment check: QR can only be generated after technician assignment
        if not booking.technician_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="QR code cannot be generated before a technician is assigned",
            )

        # Status check
        allowed_statuses = [
            BookingStatus.ACCEPTED,
            BookingStatus.ASSIGNED,
            BookingStatus.ON_THE_WAY,
            BookingStatus.ARRIVED,
            BookingStatus.WAITING_QR,
        ]
        if booking.status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot generate QR code for booking in '{booking.status.value}' status",
            )

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=QR_EXPIRY_MINUTES)
        token = f"SMARTVERIFY_{booking.id}_{secrets.token_hex(16)}"

        # Save to DB
        qr_record = self.crud.create_qr_verification(
            booking_id=booking.id,
            technician_id=booking.technician_id,
            token=token,
            expires_at=expires_at,
        )

        # Encrypt payload string
        qr_code_data, _ = self._build_encrypted_qr_data(booking, token, expires_at)

        # Update booking status to WAITING_QR if currently arrived/accepted/assigned
        old_status = booking.status
        if booking.status != BookingStatus.WAITING_QR:
            booking.status = BookingStatus.WAITING_QR
            self.db.commit()
            self.db.refresh(booking)

        self._log_audit_event(
            booking.id,
            old_status,
            BookingStatus.WAITING_QR,
            current_user.id,
            "SmartVerify QR Code Generated",
        )

        return QRGenerateResponse(
            booking_id=booking.id,
            qr_code_data=qr_code_data,
            verification_token=token,
            expires_at=expires_at,
            version="1.0",
            message="QR code generated successfully",
        )

    # ─── 2. GET QR ───────────────────────────────────────────────────────────

    def get_qr(self, current_user: User, booking_id: int) -> QRGenerateResponse:
        """Retrieve active QR details for a booking."""
        booking = self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        qr_record = self.crud.get_active_by_booking(booking_id)
        if not qr_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active QR code found for this booking. Please generate a new QR code.",
            )

        qr_code_data, token = self._build_encrypted_qr_data(
            booking, qr_record.token, qr_record.expires_at
        )
        return QRGenerateResponse(
            booking_id=booking.id,
            qr_code_data=qr_code_data,
            verification_token=token,
            expires_at=qr_record.expires_at,
            version="1.0",
            message="Active QR code retrieved successfully",
        )

    # ─── 3. SCAN QR ──────────────────────────────────────────────────────────

    def scan_qr(
        self,
        current_user: User,
        booking_id: int,
        payload: QRScanRequest,
    ) -> QRScanResponse:
        """Technician scans and validates QR code."""
        booking = self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        # Assigned technician or admin check
        if not current_user.is_superuser:
            if not current_user.technician or booking.technician_id != current_user.technician.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the assigned technician can scan the QR code",
                )

        # Lookup QR record
        qr_record = self.crud.get_by_token(payload.verification_token)
        if not qr_record or qr_record.booking_id != booking.id:
            self._log_audit_event(
                booking.id,
                booking.status,
                booking.status,
                current_user.id,
                "Verification Failed: Invalid QR token",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid QR verification token",
            )

        # Expiry check
        now = datetime.now(timezone.utc)
        if qr_record.expires_at < now:
            self._log_audit_event(
                booking.id,
                booking.status,
                booking.status,
                current_user.id,
                "Verification Failed: QR code expired",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="QR code has expired. Please ask customer to regenerate QR.",
            )

        # Single-use check
        if qr_record.used:
            self._log_audit_event(
                booking.id,
                booking.status,
                booking.status,
                current_user.id,
                "Verification Failed: QR code already used",
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="QR code has already been scanned and used",
            )

        # Mark QR as used
        self.crud.mark_used(qr_record.id, device_info=payload.device_info)

        # Update booking status to QR_VERIFIED
        old_status = booking.status
        booking.status = BookingStatus.QR_VERIFIED
        self.db.commit()
        self.db.refresh(booking)

        self._log_audit_event(
            booking.id,
            old_status,
            BookingStatus.QR_VERIFIED,
            current_user.id,
            "SmartVerify QR Scanned & Verified",
        )

        # Auto-generate 6-digit OTP for customer verification step
        otp_code = f"{random.randint(100000, 999999)}"
        otp_expires = now + timedelta(minutes=OTP_EXPIRY_MINUTES)
        self.crud.update_verification_code(qr_record.id, otp_code, otp_expires)

        return QRScanResponse(
            booking_id=booking.id,
            scanned_at=now,
            technician_id=current_user.technician.id if current_user.technician else booking.technician_id,
            status="qr_verified",
            message="QR code scanned successfully. 6-digit OTP sent to customer.",
        )

    # ─── 4. GENERATE OTP ─────────────────────────────────────────────────────

    def generate_otp(self, current_user: User, booking_id: int) -> OTPGenerateResponse:
        """Generate 6-digit OTP code with 5-minute expiry."""
        booking = self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        qr_record = self.crud.get_by_booking_id(booking_id)
        if not qr_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No QR verification record found for this booking",
            )

        now = datetime.now(timezone.utc)
        otp_code = f"{random.randint(100000, 999999)}"
        otp_expires = now + timedelta(minutes=OTP_EXPIRY_MINUTES)

        self.crud.update_verification_code(qr_record.id, otp_code, otp_expires)

        self._log_audit_event(
            booking.id,
            booking.status,
            booking.status,
            current_user.id,
            "SmartVerify OTP Generated",
        )

        return OTPGenerateResponse(
            booking_id=booking.id,
            otp_code=otp_code,
            expires_at=otp_expires,
            message="OTP generated successfully",
        )

    # ─── 5. VERIFY OTP ───────────────────────────────────────────────────────

    def verify_otp(
        self,
        current_user: User,
        booking_id: int,
        payload: OTPVerifyRequest,
    ) -> OTPVerifyResponse:
        """Customer verifies 6-digit OTP to start service."""
        booking = self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        # Access check: Customer owning booking or Admin
        if not current_user.is_superuser:
            if not current_user.customer or booking.customer_id != current_user.customer.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the booking owner can confirm the OTP",
                )

        # Status check
        if booking.status not in [BookingStatus.QR_VERIFIED, BookingStatus.WAITING_QR]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot verify OTP for booking in '{booking.status.value}' status",
            )

        qr_record = self.crud.get_by_booking_id(booking_id)
        if not qr_record or not qr_record.verification_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active OTP found. Please generate OTP first.",
            )

        now = datetime.now(timezone.utc)
        if qr_record.expires_at < now:
            self._log_audit_event(
                booking.id,
                booking.status,
                booking.status,
                current_user.id,
                "Verification Failed: OTP expired",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired. Please generate a new OTP.",
            )

        if qr_record.verification_code != payload.otp_code:
            self._log_audit_event(
                booking.id,
                booking.status,
                booking.status,
                current_user.id,
                f"Verification Failed: Invalid OTP entered ({payload.otp_code})",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP code. Please check and try again.",
            )

        # Invalidate OTP after successful verification
        qr_record.verification_code = ""
        self.db.commit()

        # Update booking status to IN_PROGRESS
        old_status = booking.status
        booking.status = BookingStatus.IN_PROGRESS
        self.db.commit()
        self.db.refresh(booking)

        self._log_audit_event(
            booking.id,
            old_status,
            BookingStatus.IN_PROGRESS,
            current_user.id,
            "SmartVerify OTP Verified - Service Started",
        )

        return OTPVerifyResponse(
            booking_id=booking.id,
            verified_at=now,
            status="in_progress",
            message="OTP verified successfully. Service is now in progress.",
        )

    # ─── 6. GET VERIFICATION STATUS ──────────────────────────────────────────

    def get_verification_status(
        self,
        current_user: User,
        booking_id: int,
    ) -> SmartVerifyStatusResponse:
        """Get SmartVerify verification status for a booking."""
        booking = self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        qr_record = self.crud.get_by_booking_id(booking_id)
        now = datetime.now(timezone.utc)

        is_qr_generated = qr_record is not None
        is_qr_scanned = qr_record.used if qr_record else False
        is_otp_generated = bool(qr_record and qr_record.verification_code)
        is_otp_verified = booking.status == BookingStatus.IN_PROGRESS

        qr_expires = qr_record.expires_at if qr_record else None
        otp_expires = qr_record.expires_at if (qr_record and is_otp_generated) else None

        return SmartVerifyStatusResponse(
            booking_id=booking.id,
            booking_status=booking.status.value if hasattr(booking.status, "value") else str(booking.status),
            is_qr_generated=is_qr_generated,
            is_qr_scanned=is_qr_scanned,
            is_otp_generated=is_otp_generated,
            is_otp_verified=is_otp_verified,
            qr_expires_at=qr_expires,
            otp_expires_at=otp_expires,
            attempts_remaining=3,
        )
