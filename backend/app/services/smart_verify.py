"""
SmartVerify Service Layer for HomiQ Backend.

Handles the dual-verification flow:
1. PIN generation (Customer receives)
2. PIN verification (Technician enters)
3. QR generation (Technician shows)
4. QR scanning (Customer scans)
5. Dual confirmation (Both confirm)
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
from passlib.context import CryptContext

from app.core.config import settings
from app.crud.qr import QRVerificationCRUD
from app.models.auth import User
from app.models.bookings import Booking, BookingStatus, BookingStatusLog
from app.schemas.bookings import (
    GeneratePinResponse,
    VerifyPinRequest,
    VerifyPinResponse,
    QRGenerateResponse,
    QRScanRequest,
    QRScanResponse,
    DualConfirmResponse,
    SmartVerifyStatusResponse,
)

# Configuration defaults
QR_EXPIRY_MINUTES = 15
PIN_EXPIRY_MINUTES = 15
MAX_PIN_ATTEMPTS = 5
TOKEN_SECRET_KEY = getattr(settings, "SECRET_KEY", "homiq_smartverify_secret_key_2026")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SmartVerifyService:
    """Service layer enforcing SmartVerify dual-verification security rules."""

    def __init__(self, db: Session):
        self.db = db
        self.crud = QRVerificationCRUD(db)

    # ─── ENCRYPTION & LOGGING HELPERS ─────────────────────────────────

    def _generate_signature(self, payload_str: str) -> str:
        return hmac.new(
            TOKEN_SECRET_KEY.encode(),
            payload_str.encode(),
            hashlib.sha256,
        ).hexdigest()

    def _build_encrypted_qr_data(
        self, booking: Booking, token: str, expires_at: datetime
    ) -> tuple[str, str]:
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

        envelope = {"data": raw_payload, "sig": signature}
        encoded_data = base64.urlsafe_b64encode(json.dumps(envelope).encode()).decode()
        return encoded_data, token

    def _verify_qr_data(self, qr_code_data: str) -> dict[str, Any]:
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
        self, booking_id: int, old_status: Optional[BookingStatus], new_status: BookingStatus, user_id: Optional[int], note: str
    ) -> None:
        log_entry = BookingStatusLog(
            booking_id=booking_id,
            old_status=old_status,
            new_status=new_status,
            changed_by_user_id=user_id,
            reason=note,
        )
        self.db.add(log_entry)
        self.db.commit()

    # ─── 1. GENERATE PIN (Backend/Customer) ──────────────────────────

    def generate_pin(self, current_user: User, booking_id: int) -> GeneratePinResponse:
        booking = self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if not current_user.is_superuser:
            if not current_user.customer or booking.customer_id != current_user.customer.id:
                raise HTTPException(status_code=403, detail="Only customer can generate PIN")

        if booking.status not in [BookingStatus.ARRIVED, BookingStatus.WAITING_QR]:
            raise HTTPException(status_code=409, detail="Technician must arrive before generating PIN")

        pin_code = f"{random.randint(100000, 999999)}"
        pin_hash = pwd_context.hash(pin_code)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=PIN_EXPIRY_MINUTES)

        qr_record = self.crud.get_by_booking_id(booking_id)
        if not qr_record:
            qr_record = self.crud.create_qr_verification(
                booking_id=booking.id,
                technician_id=booking.technician_id,
                token="",
                expires_at=expires_at,
            )

        self.crud.update_pin(qr_record.id, pin_hash, expires_at)
        
        # We can change status to WAITING_QR or keep ARRIVED
        if booking.status == BookingStatus.ARRIVED:
            booking.status = BookingStatus.WAITING_QR
            self.db.commit()

        self._log_audit_event(booking.id, booking.status, booking.status, current_user.id, "PIN Generated for Customer")

        return GeneratePinResponse(
            booking_id=booking.id,
            message="PIN generated successfully",
            pin_expires_at=expires_at,
            pin_code=pin_code
        )

    # ─── 2. VERIFY PIN (Technician) ──────────────────────────────────

    def verify_pin(self, current_user: User, booking_id: int, payload: VerifyPinRequest) -> VerifyPinResponse:
        booking = self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if not current_user.is_superuser:
            if not current_user.technician or booking.technician_id != current_user.technician.id:
                raise HTTPException(status_code=403, detail="Only assigned technician can verify PIN")

        qr_record = self.crud.get_by_booking_id(booking_id)
        if not qr_record or not qr_record.customer_pin_hash:
            raise HTTPException(status_code=400, detail="PIN not generated yet")

        now = datetime.now(timezone.utc)
        if qr_record.pin_expires_at and qr_record.pin_expires_at.tzinfo is None:
            now = now.replace(tzinfo=None)

        if qr_record.pin_expires_at and qr_record.pin_expires_at < now:
            raise HTTPException(status_code=400, detail="PIN expired")

        if qr_record.pin_attempt_count >= MAX_PIN_ATTEMPTS:
            raise HTTPException(status_code=400, detail="Too many failed PIN attempts")

        if not pwd_context.verify(payload.pin, qr_record.customer_pin_hash):
            self.crud.increment_pin_attempt(qr_record.id)
            raise HTTPException(status_code=400, detail="Invalid PIN")

        self.crud.mark_pin_verified(qr_record.id)
        self._log_audit_event(booking.id, booking.status, booking.status, current_user.id, "Customer PIN Verified by Technician")

        return VerifyPinResponse(
            booking_id=booking.id,
            message="PIN verified successfully",
            verified_at=now
        )

    # ─── 3. GENERATE QR (Technician) ─────────────────────────────────

    def generate_qr(self, current_user: User, booking_id: int) -> QRGenerateResponse:
        booking = self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if not current_user.is_superuser:
            if not current_user.technician or booking.technician_id != current_user.technician.id:
                raise HTTPException(status_code=403, detail="Only assigned technician can generate QR")

        qr_record = self.crud.get_by_booking_id(booking_id)
        if not qr_record or not qr_record.customer_pin_verified_at:
            raise HTTPException(status_code=400, detail="PIN must be verified before generating QR")

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=QR_EXPIRY_MINUTES)
        token = f"SMARTVERIFY_{booking.id}_{secrets.token_hex(16)}"

        qr_record.token = token
        qr_record.expires_at = expires_at
        qr_record.used = False
        self.db.commit()
        self.db.refresh(qr_record)

        qr_code_data, _ = self._build_encrypted_qr_data(booking, token, expires_at)
        self._log_audit_event(booking.id, booking.status, booking.status, current_user.id, "Technician QR Generated")

        return QRGenerateResponse(
            booking_id=booking.id,
            qr_code_data=qr_code_data,
            verification_token=token,
            expires_at=expires_at,
            version="1.0",
            message="QR code generated successfully"
        )

    def get_qr(self, current_user: User, booking_id: int) -> QRGenerateResponse:
        booking = self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        qr_record = self.crud.get_active_by_booking(booking_id)
        if not qr_record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active QR code found")
        qr_code_data, token = self._build_encrypted_qr_data(booking, qr_record.token, qr_record.expires_at)
        return QRGenerateResponse(
            booking_id=booking.id,
            qr_code_data=qr_code_data,
            verification_token=token,
            expires_at=qr_record.expires_at,
            version="1.0",
            message="Active QR code retrieved successfully",
        )

    # ─── 4. SCAN QR (Customer) ───────────────────────────────────────

    def scan_qr(self, current_user: User, booking_id: int, payload: QRScanRequest) -> QRScanResponse:
        booking = self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if not current_user.is_superuser:
            if not current_user.customer or booking.customer_id != current_user.customer.id:
                raise HTTPException(status_code=403, detail="Only customer can scan QR")

        qr_record = self.crud.get_by_token(payload.verification_token)
        if not qr_record or qr_record.booking_id != booking.id:
            raise HTTPException(status_code=400, detail="Invalid QR token")

        now = datetime.now(timezone.utc)
        if qr_record.expires_at and qr_record.expires_at.tzinfo is None:
            now = now.replace(tzinfo=None)

        if qr_record.expires_at and qr_record.expires_at < now:
            raise HTTPException(status_code=400, detail="QR code expired")

        if qr_record.used:
            raise HTTPException(status_code=409, detail="QR already used")

        self.crud.mark_used(qr_record.id, device_info=payload.device_info)
        self.crud.mark_qr_scanned(qr_record.id)

        old_status = booking.status
        booking.status = BookingStatus.QR_VERIFIED
        self.db.commit()
        self.db.refresh(booking)

        self._log_audit_event(booking.id, old_status, BookingStatus.QR_VERIFIED, current_user.id, "Technician QR Scanned by Customer")

        return QRScanResponse(
            booking_id=booking.id,
            scanned_at=now,
            technician_id=booking.technician_id,
            status="qr_verified",
            message="QR scanned successfully"
        )

    # ─── 5. DUAL CONFIRM (Both) ──────────────────────────────────────

    def customer_confirm(self, current_user: User, booking_id: int) -> DualConfirmResponse:
        booking = self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if not current_user.is_superuser:
            if not current_user.customer or booking.customer_id != current_user.customer.id:
                raise HTTPException(status_code=403, detail="Only customer can confirm")

        qr_record = self.crud.get_by_booking_id(booking_id)
        if not qr_record or not qr_record.technician_qr_verified_at:
            raise HTTPException(status_code=400, detail="Must scan QR first")

        self.crud.mark_customer_confirmed(qr_record.id)
        self.db.refresh(qr_record)

        if qr_record.verification_status == "verified":
            booking.status = BookingStatus.IN_PROGRESS # Or READY_TO_START
            self.db.commit()
            self._log_audit_event(booking.id, BookingStatus.QR_VERIFIED, BookingStatus.IN_PROGRESS, current_user.id, "SmartVerify Completed")

        return DualConfirmResponse(
            booking_id=booking.id,
            message="Customer confirmed",
            verification_status=qr_record.verification_status
        )

    def technician_confirm(self, current_user: User, booking_id: int) -> DualConfirmResponse:
        booking = self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if not current_user.is_superuser:
            if not current_user.technician or booking.technician_id != current_user.technician.id:
                raise HTTPException(status_code=403, detail="Only technician can confirm")

        qr_record = self.crud.get_by_booking_id(booking_id)
        if not qr_record or not qr_record.technician_qr_verified_at:
            raise HTTPException(status_code=400, detail="Must scan QR first")

        self.crud.mark_technician_confirmed(qr_record.id)
        self.db.refresh(qr_record)

        if qr_record.verification_status == "verified":
            booking.status = BookingStatus.IN_PROGRESS # Or READY_TO_START
            self.db.commit()
            self._log_audit_event(booking.id, BookingStatus.QR_VERIFIED, BookingStatus.IN_PROGRESS, current_user.id, "SmartVerify Completed")

        return DualConfirmResponse(
            booking_id=booking.id,
            message="Technician confirmed",
            verification_status=qr_record.verification_status
        )

    # ─── 6. STATUS GETTER ────────────────────────────────────────────

    def get_verification_status(self, current_user: User, booking_id: int) -> SmartVerifyStatusResponse:
        booking = self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        qr_record = self.crud.get_by_booking_id(booking_id)

        is_pin_generated = bool(qr_record and qr_record.customer_pin_hash)
        is_pin_verified = bool(qr_record and qr_record.customer_pin_verified_at)
        is_qr_generated = bool(qr_record and qr_record.token)
        is_qr_scanned = bool(qr_record and qr_record.technician_qr_verified_at)
        is_customer_confirmed = bool(qr_record and qr_record.customer_confirmed_at)
        is_technician_confirmed = bool(qr_record and qr_record.technician_confirmed_at)
        is_fully_verified = bool(qr_record and qr_record.verification_status == "verified")

        return SmartVerifyStatusResponse(
            booking_id=booking.id,
            booking_status=booking.status.value if hasattr(booking.status, "value") else str(booking.status),
            is_pin_generated=is_pin_generated,
            is_pin_verified=is_pin_verified,
            is_qr_generated=is_qr_generated,
            is_qr_scanned=is_qr_scanned,
            is_customer_confirmed=is_customer_confirmed,
            is_technician_confirmed=is_technician_confirmed,
            is_fully_verified=is_fully_verified,
            qr_expires_at=qr_record.expires_at if qr_record else None,
            pin_expires_at=qr_record.pin_expires_at if qr_record else None,
            attempts_remaining=MAX_PIN_ATTEMPTS - (qr_record.pin_attempt_count if qr_record else 0),
        )
