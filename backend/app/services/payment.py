"""
Payment service layer.

Handles all payment business logic:
- Creates Razorpay orders and persists payment records
- Verifies Razorpay payment signatures (callback / webhook)
- Role-scoped listing (admin sees all, customers see own)
- Refund processing (admin-only)
- Graceful error handling with standardised HTTP exceptions

Uses the RazorpayClient wrapper from app.integrations.razorpay for
all Razorpay API interactions.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.payment import PaymentCRUD
from app.crud.customer import CustomerCRUD
from app.integrations.razorpay import RazorpayClient
from app.models.auth import User
from app.models.payments import Payment, PaymentMethod, PaymentStatus
from app.schemas.payments import (
    PaymentCreateOrder,
    PaymentListResponse,
    PaymentResponse,
    PaymentVerify,
)

logger = logging.getLogger(__name__)


class PaymentService:
    """Service layer for payment operations."""

    def __init__(self, db: Session):
        self.db = db
        self.crud = PaymentCRUD(db)
        self.customer_crud = CustomerCRUD(db)
        self.razorpay_client = RazorpayClient()

    # ─────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────

    def _get_customer_id(self, current_user: User) -> int:
        """Resolve the Customer record for the current user."""
        customer = self.customer_crud.get_by_user_id(current_user.id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found.",
            )
        return customer.id

    def _resolve_payment_method(self, razorpay_payment_id: str) -> PaymentMethod:
        """Fetch the payment method from Razorpay for audit purposes.

        Falls back to UNKNOWN if the API call fails so the payment
        flow is not blocked by a non-critical enrichment.
        """
        try:
            details = self.razorpay_client.fetch_payment(razorpay_payment_id)
            method_str = details.get("method", "").lower()
            method_map = {
                "card": PaymentMethod.CARD,
                "upi": PaymentMethod.UPI,
                "netbanking": PaymentMethod.NETBANKING,
                "wallet": PaymentMethod.WALLET,
                "emi": PaymentMethod.EMI,
            }
            return method_map.get(method_str, PaymentMethod.UNKNOWN)
        except Exception as exc:
            logger.warning(
                "Could not fetch payment method for %s: %s",
                razorpay_payment_id,
                exc,
            )
            return PaymentMethod.UNKNOWN

    # ── CREATE ORDER ────────────────────────────────────────────────

    def create_order(
        self,
        current_user: User,
        payload: PaymentCreateOrder,
    ) -> dict[str, Any]:
        """
        Create a Razorpay order and persist a payment record.

        1. Validate the booking exists and belongs to the customer.
        2. Check for an existing CREATED payment (idempotency).
        3. Create an order on Razorpay with the booking's final_price.
        4. Persist a Payment record with status=CREATED.

        Args:
            current_user: Authenticated user (JWT, must be a customer).
            payload: Contains the booking_id.

        Returns:
            dict with Razorpay order details (id, amount, currency, key_id, etc.)

        Raises:
            404: If the customer profile or booking is not found.
            403: If the booking does not belong to the customer.
            400: If the booking does not have a valid final_price.
        """
        from app.crud.booking import BookingCRUD

        customer_id = self._get_customer_id(current_user)
        booking_crud = BookingCRUD(self.db)
        booking = booking_crud.get_booking(payload.booking_id)

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        if booking.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This booking does not belong to you.",
            )

        # Validate payable amount
        # Prefer final_price; fall back to estimated_price when set by the customer.
        payable = booking.final_price or booking.estimated_price or 0.0
        if payable <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking does not have a valid price to pay.",
            )

        # Convert ₹ to paise
        amount_paise = int(payable * 100)

        # ── Idempotency: resume an existing CREATED order ──────────
        existing = self.crud.get_by_booking(payload.booking_id)
        if existing and existing.status == PaymentStatus.CREATED and existing.razorpay_order_id:
            logger.info(
                "Resuming existing CREATED order %s for booking %d",
                existing.razorpay_order_id,
                payload.booking_id,
            )
            return {
                "id": existing.razorpay_order_id,
                "amount": int(existing.amount * 100),
                "currency": existing.currency,
                "key_id": settings.RAZORPAY_KEY_ID,
                "payment_id": existing.id,
                "status": "created",
            }


        # ── Create Razorpay order via the integration wrapper ──────
        razorpay_order = self.razorpay_client.create_order(
            amount_paise=amount_paise,
            currency="INR",
            receipt=booking.booking_number,
            notes={
                "booking_id": str(booking.id),
                "customer_id": str(customer_id),
            },
        )

        # ── Persist payment record ────────────────────────────────
        payment_data: dict[str, Any] = {
            "booking_id": booking.id,
            "customer_id": customer_id,
            "amount": payable,
            "currency": "INR",
            "razorpay_order_id": razorpay_order["id"],
            "payment_method": PaymentMethod.UNKNOWN,
            "status": PaymentStatus.CREATED,
        }
        payment = self.crud.create(payment_data)

        logger.info(
            "Created Razorpay order %s (₹%.2f) for booking %d",
            razorpay_order["id"],
            payable,
            booking.id,
        )

        return {
            "id": razorpay_order["id"],
            "amount": razorpay_order["amount"],
            "currency": razorpay_order["currency"],
            "key_id": settings.RAZORPAY_KEY_ID,
            "payment_id": payment.id,
            "status": "created",
        }

    # ── VERIFY PAYMENT ──────────────────────────────────────────────

    def verify_payment(
        self,
        payload: PaymentVerify,
    ) -> PaymentResponse:
        """
        Verify a Razorpay payment signature and mark payment as PAID.

        Steps:
        1. Locate the payment record by razorpay_order_id.
        2. Verify the HMAC-SHA256 signature using the server secret.
        3. Resolve the payment method from Razorpay.
        4. Mark payment as PAID and update booking payment_status.

        Args:
            payload: Contains razorpay_order_id, razorpay_payment_id,
                     razorpay_signature.

        Returns:
            PaymentResponse with updated payment details.

        Raises:
            404: If the payment record is not found.
            400: If the signature is invalid or payment already processed.
        """
        payment = self.crud.get_by_order_id(payload.razorpay_order_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment order not found.",
            )

        if payment.status == PaymentStatus.PAID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment has already been verified and is paid.",
            )

        # ── Verify signature using the integration wrapper ──────────
        is_valid = self.razorpay_client.verify_payment(
            order_id=payload.razorpay_order_id,
            payment_id=payload.razorpay_payment_id,
            signature=payload.razorpay_signature,
        )

        if not is_valid:
            self.crud.mark_failed(payment)
            logger.warning(
                "Invalid signature for order %s", payload.razorpay_order_id
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment signature.",
            )

        # ── Resolve payment method from Razorpay ───────────────────
        payment_method = self._resolve_payment_method(payload.razorpay_payment_id)

        # ── Mark payment as paid ───────────────────────────────────
        updated = self.crud.mark_paid(
            payment=payment,
            razorpay_payment_id=payload.razorpay_payment_id,
            razorpay_signature=payload.razorpay_signature,
            payment_method=payment_method,
        )

        # ── Update booking payment_status ──────────────────────────
        from app.crud.booking import BookingCRUD
        from app.models.bookings import PaymentStatus as BookingPaymentStatus

        booking_crud = BookingCRUD(self.db)
        booking_crud.update_booking(
            booking_id=payment.booking_id,
            data={"payment_status": BookingPaymentStatus.PAID},
        )

        logger.info(
            "Payment %s verified for order %s (booking %d)",
            payload.razorpay_payment_id,
            payload.razorpay_order_id,
            payment.booking_id,
        )

        return PaymentResponse.model_validate(updated)

    # ── GET SINGLE PAYMENT ──────────────────────────────────────────

    def get_payment(
        self,
        current_user: User,
        payment_id: int,
    ) -> PaymentResponse:
        """
        Retrieve a single payment by ID.

        Access is restricted to:
        - The customer who owns the payment.
        - Any admin (superuser).

        Args:
            current_user: Authenticated user (JWT).
            payment_id: Unique payment ID.

        Returns:
            PaymentResponse with full payment details.

        Raises:
            404: If the payment does not exist.
            403: If the user is not authorised.
        """
        payment = self.crud.get(payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found.",
            )

        is_owner = payment.customer and payment.customer.user_id == current_user.id
        if not (is_owner or current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this payment.",
            )

        return PaymentResponse.model_validate(payment)

    # ── LIST PAYMENTS ───────────────────────────────────────────────

    def list_payments(
        self,
        current_user: User,
        offset: int = 0,
        limit: int = 100,
    ) -> PaymentListResponse:
        """
        List payments scoped to the current user's role.

        - **Admin**: sees all payments.
        - **Customer**: sees only their own payments.

        Args:
            current_user: Authenticated user (JWT).
            offset: Number of records to skip (pagination).
            limit: Maximum number of records to return.

        Returns:
            PaymentListResponse with items and total count.
        """
        if current_user.is_superuser:
            payments = (
                self.db.execute(
                    select(Payment)
                    .order_by(Payment.created_at.desc())
                    .offset(offset)
                    .limit(limit)
                )
                .scalars()
                .all()
            )
            total = self.db.scalar(select(func.count(Payment.id))) or 0
        else:
            customer = self.customer_crud.get_by_user_id(current_user.id)
            if customer:
                payments = self.crud.list_customer_payments(
                    customer_id=customer.id,
                    offset=offset,
                    limit=limit,
                )
                total = self.crud.count_customer_payments(
                    customer_id=customer.id
                )
            else:
                payments = []
                total = 0

        return PaymentListResponse(
            items=[PaymentResponse.model_validate(p) for p in payments],
            total=int(total),
        )

    # ── REFUND (Admin only) ─────────────────────────────────────────

    def refund_payment(
        self,
        current_user: User,
        payment_id: int,
    ) -> PaymentResponse:
        """
        Process a refund for a paid payment.

        **Admin-only.**  Initiates a refund via the RazorpayClient
        wrapper and updates the payment status to REFUNDED.

        Args:
            current_user: Authenticated user (JWT, must be admin).
            payment_id: Unique payment ID.

        Returns:
            PaymentResponse with updated payment details.

        Raises:
            403: If the user is not an admin.
            404: If the payment is not found.
            400: If the payment is not in PAID status.
        """
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required.",
            )

        payment = self.crud.get(payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found.",
            )

        if payment.status != PaymentStatus.PAID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot refund payment with status "
                    f"'{payment.status.value}'. Only 'paid' payments can be refunded."
                ),
            )

        # ── Initiate refund via RazorpayClient wrapper ──────────────
        if payment.razorpay_payment_id:
            self.razorpay_client.process_refund(payment.razorpay_payment_id)
            logger.info(
                "Refund initiated for payment %s (Razorpay ID: %s)",
                payment_id,
                payment.razorpay_payment_id,
            )

        # ── Mark as refunded locally ───────────────────────────────
        updated = self.crud.mark_refunded(payment)

        # ── Update booking payment_status to REFUNDED ─────────────
        from app.crud.booking import BookingCRUD
        from app.models.bookings import PaymentStatus as BookingPaymentStatus

        booking_crud = BookingCRUD(self.db)
        booking_crud.update_booking(
            booking_id=payment.booking_id,
            data={"payment_status": BookingPaymentStatus.REFUNDED},
        )

        return PaymentResponse.model_validate(updated)

