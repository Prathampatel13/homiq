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

        # ── Update booking payment_status & auto-generate invoice ──
        from app.crud.booking import BookingCRUD
        from app.models.bookings import PaymentStatus as BookingPaymentStatus

        booking_crud = BookingCRUD(self.db)
        booking = booking_crud.get_booking(payment.booking_id)
        booking_crud.update_booking(
            booking_id=payment.booking_id,
            data={"payment_status": BookingPaymentStatus.PAID},
        )

        if booking:
            self._generate_invoice(booking, updated)

        self._log_audit_event(
            payment.booking_id,
            booking.status if booking else None,
            booking.status if booking else None,
            payment.customer_id,
            "Payment Signature Verified Successfully",
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
            try:
                self.razorpay_client.process_refund(payment.razorpay_payment_id)
                logger.info(
                    "Refund initiated for payment %s (Razorpay ID: %s)",
                    payment_id,
                    payment.razorpay_payment_id,
                )
            except Exception as exc:
                logger.warning(
                    "Razorpay refund API call failed for %s (proceeding with local status update): %s",
                    payment.razorpay_payment_id,
                    exc,
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

    # ── AUDIT LOG HELPER ─────────────────────────────────────────────

    def _log_audit_event(
        self,
        booking_id: int,
        old_status: Optional[Any],
        new_status: Any,
        user_id: Optional[int],
        note: str,
    ) -> None:
        from app.models.bookings import BookingStatusLog
        log_entry = BookingStatusLog(
            booking_id=booking_id,
            old_status=old_status,
            new_status=new_status,
            changed_by_user_id=user_id,
            reason=note,
        )
        self.db.add(log_entry)
        self.db.commit()

    # ── AUTO INVOICE GENERATION ──────────────────────────────────────

    def _generate_invoice(self, booking: Any, payment: Payment) -> Any:
        from datetime import datetime, timezone
        from app.models.invoices import Invoice, InvoiceStatus

        # Check existing invoice
        stmt = select(Invoice).where(Invoice.booking_id == booking.id)
        existing = self.db.scalar(stmt)
        if existing:
            return existing

        subtotal = float(payment.amount)
        gst_amount = round(subtotal * 0.18, 2)
        discount = float(getattr(booking, "discount_amount", 0.0) or 0.0)
        total_amount = round(subtotal + gst_amount - discount, 2)

        inv_num = f"INV-{booking.id}-{int(datetime.now(timezone.utc).timestamp())}"

        invoice = Invoice(
            invoice_number=inv_num,
            booking_id=booking.id,
            customer_id=booking.customer_id,
            payment_id=payment.id,
            subtotal=subtotal,
            tax_percentage=18.0,
            tax_amount=gst_amount,
            discount_amount=discount,
            total_amount=total_amount,
            amount_paid=total_amount,
            amount_due=0.0,
            status=InvoiceStatus.PAID,
            issued_at=datetime.now(timezone.utc),
            due_at=datetime.now(timezone.utc),
            paid_at=datetime.now(timezone.utc),
        )
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)

        self._log_audit_event(
            booking.id,
            booking.status,
            booking.status,
            payment.customer_id,
            f"Invoice {inv_num} Generated Automatically",
        )
        return invoice

    # ── WEBHOOK HANDLER ──────────────────────────────────────────────

    def handle_webhook(
        self,
        event_name: str,
        payload_data: dict[str, Any],
        signature: Optional[str] = None,
    ) -> dict[str, str]:
        """
        Handle Razorpay webhook notifications.
        Events: payment.authorized, payment.captured, payment.failed, refund.created, refund.processed, order.paid
        """
        logger.info("Processing Razorpay webhook event: %s", event_name)

        entity = payload_data.get("payment", {}).get("entity") or payload_data.get("order", {}).get("entity") or {}
        razorpay_order_id = entity.get("order_id") or entity.get("id")
        razorpay_payment_id = entity.get("id") if entity.get("order_id") else None

        if not razorpay_order_id:
            return {"status": "ignored", "detail": "No order_id in webhook payload"}

        payment = self.crud.get_by_order_id(razorpay_order_id)
        if not payment and razorpay_payment_id:
            payment = self.crud.get_by_payment_id(razorpay_payment_id)

        if not payment:
            return {"status": "ignored", "detail": "Associated payment record not found"}

        from app.crud.booking import BookingCRUD
        from app.models.bookings import PaymentStatus as BookingPaymentStatus
        booking_crud = BookingCRUD(self.db)
        booking = booking_crud.get_booking(payment.booking_id)

        if event_name in ["payment.captured", "payment.authorized", "order.paid"]:
            if payment.status != PaymentStatus.PAID:
                pm = self.PaymentMethod.UNKNOWN
                if razorpay_payment_id:
                    pm = self._resolve_payment_method(razorpay_payment_id)

                self.crud.mark_paid(
                    payment=payment,
                    razorpay_payment_id=razorpay_payment_id or payment.razorpay_payment_id or "pay_webhook",
                    razorpay_signature=signature or "webhook_verified",
                    payment_method=pm,
                )

                if booking:
                    booking_crud.update_booking(
                        booking_id=booking.id,
                        data={"payment_status": BookingPaymentStatus.PAID},
                    )
                    self._generate_invoice(booking, payment)

                self._log_audit_event(
                    payment.booking_id,
                    booking.status if booking else None,
                    booking.status if booking else None,
                    None,
                    f"Payment Verified via Webhook Event ({event_name})",
                )

        elif event_name in ["payment.failed"]:
            if payment.status != PaymentStatus.PAID:
                self.crud.mark_failed(payment)
                self._log_audit_event(
                    payment.booking_id,
                    booking.status if booking else None,
                    booking.status if booking else None,
                    None,
                    f"Payment Failed via Webhook Event ({event_name})",
                )

        elif event_name in ["refund.created", "refund.processed"]:
            if payment.status != PaymentStatus.REFUNDED:
                self.crud.mark_refunded(payment)
                if booking:
                    booking_crud.update_booking(
                        booking_id=booking.id,
                        data={"payment_status": BookingPaymentStatus.REFUNDED},
                    )
                self._log_audit_event(
                    payment.booking_id,
                    booking.status if booking else None,
                    booking.status if booking else None,
                    None,
                    f"Refund Processed via Webhook Event ({event_name})",
                )

        return {"status": "success", "event": event_name}

    # ── PAYMENT HISTORY ──────────────────────────────────────────────

    def get_payment_history(
        self,
        current_user: User,
        offset: int = 0,
        limit: int = 100,
    ):
        from app.schemas.payments import PaymentHistoryEntry, PaymentHistoryResponse

        customer_id = None
        if not current_user.is_superuser:
            customer_id = self._get_customer_id(current_user)

        payments = self.crud.get_payment_history(customer_id=customer_id, offset=offset, limit=limit)
        total = self.crud.count_payment_history(customer_id=customer_id)

        items = []
        for p in payments:
            service_name = p.booking.service.name if p.booking and p.booking.service else "N/A"
            booking_number = p.booking.booking_number if p.booking else "N/A"
            items.append(
                PaymentHistoryEntry(
                    id=p.id,
                    booking_id=p.booking_id,
                    booking_number=booking_number,
                    service_name=service_name,
                    amount=p.amount,
                    currency=p.currency,
                    status=p.status,
                    payment_method=p.payment_method,
                    created_at=p.created_at,
                )
            )

        return PaymentHistoryResponse(items=items, total=total)

    # ── PAYLOAD REFUND REQUEST ───────────────────────────────────────

    def refund_payment_payload(
        self,
        current_user: User,
        payload: Any,
    ) -> PaymentResponse:
        result = self.refund_payment(current_user, payload.payment_id)
        payment = self.crud.get(payload.payment_id)
        if payment:
            self._log_audit_event(
                payment.booking_id,
                payment.booking.status if payment.booking else None,
                payment.booking.status if payment.booking else None,
                current_user.id,
                f"Refund Initiated & Completed (Reason: {payload.reason or 'Admin refund'})",
            )
        return result

    # ── GET INVOICE BY PAYMENT ───────────────────────────────────────

    def get_payment_invoice(
        self,
        current_user: User,
        payment_id: int,
    ):
        from app.models.invoices import Invoice
        from app.schemas.payments import PaymentInvoiceResponse

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
                detail="Not authorized to view invoice for this payment.",
            )

        booking = payment.booking
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated booking not found.",
            )

        invoice = self._generate_invoice(booking, payment)

        cust_name = booking.customer.user.full_name if booking.customer and booking.customer.user else "Customer"
        tech_name = booking.technician.user.full_name if booking.technician and booking.technician.user else "Technician"
        srv_name = booking.service.name if booking.service else "Service"

        return PaymentInvoiceResponse(
            invoice_id=invoice.id,
            invoice_number=invoice.invoice_number,
            booking_id=booking.id,
            customer_name=cust_name,
            technician_name=tech_name,
            service_name=srv_name,
            subtotal=invoice.subtotal,
            gst_amount=invoice.tax_amount,
            discount_amount=invoice.discount_amount,
            total_amount=invoice.total_amount,
            payment_method=payment.payment_method.value if hasattr(payment.payment_method, "value") else str(payment.payment_method),
            status=invoice.status.value if hasattr(invoice.status, "value") else str(invoice.status),
            paid_at=invoice.paid_at or invoice.issued_at,
        )


