
"""
Payment management endpoints.

All endpoints are JWT-protected and require a valid Bearer token.
- Customers can create orders, verify payments, and list own payments.
- Admins can list all payments, view any payment, and process refunds.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user, get_current_admin
from app.schemas.payments import (
    PaymentCreateOrder,
    PaymentHistoryResponse,
    PaymentInvoiceResponse,
    PaymentListResponse,
    PaymentRefundRequest,
    PaymentResponse,
    PaymentVerify,
    PaymentWebhookPayload,
)
from app.services.payment import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


# ─── CREATE ORDER ───────────────────────────────────────────────────────


@router.post(
    "/create-order",
    summary="Create a Razorpay order",
    description=(
        "Creates a Razorpay order for a given booking and persists a payment "
        "record with status 'created'. If a 'created' payment already exists "
        "for the booking, the existing order details are returned so the "
        "frontend can resume without creating a duplicate."
    ),
    response_description="Razorpay order details (id, amount, currency, key_id).",
)
def create_order(
    payload: PaymentCreateOrder,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create a Razorpay order for a booking."""
    return PaymentService(db).create_order(current_user, payload)


# ─── VERIFY PAYMENT ─────────────────────────────────────────────────────


@router.post(
    "/verify",
    response_model=PaymentResponse,
    summary="Verify a Razorpay payment",
    description=(
        "Verifies the Razorpay payment signature. On success, the payment "
        "status is updated to 'paid' and the associated booking's "
        "payment_status is updated accordingly."
    ),
    response_description="The updated payment record with status 'paid'.",
)
def verify_payment(
    payload: PaymentVerify,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Verify a Razorpay payment signature."""
    return PaymentService(db).verify_payment(payload)


# ─── WEBHOOK HANDLER ─────────────────────────────────────────────────────


@router.post(
    "/webhook",
    summary="Razorpay Webhook Handler",
    description="Processes asynchronous Razorpay webhook events with signature verification.",
)
def razorpay_webhook(
    payload: dict[str, Any],
    x_razorpay_signature: Optional[str] = Header(None, alias="X-Razorpay-Signature"),
    db: Session = Depends(get_db),
) -> Any:
    """Process Razorpay webhook notifications."""
    event_name = payload.get("event", "unknown")
    event_payload = payload.get("payload", {})
    return PaymentService(db).handle_webhook(event_name, event_payload, x_razorpay_signature)


# ─── PAYMENT HISTORY ────────────────────────────────────────────────────


@router.get(
    "/history",
    response_model=PaymentHistoryResponse,
    summary="Payment transaction history",
    description="Returns detailed transaction history for the authenticated customer or all history for admin.",
)
def payment_history(
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get payment transaction history."""
    return PaymentService(db).get_payment_history(current_user, offset=offset, limit=limit)


# ─── LIST PAYMENTS ──────────────────────────────────────────────────────


@router.get(
    "/",
    response_model=PaymentListResponse,
    summary="List payments",
    description=(
        "Returns a paginated list of payments visible to the current user. "
        "Admins see all payments. Customers see only their own payments."
    ),
    response_description="Paginated list of payments with total count.",
)
def list_payments(
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """List payments with pagination, scoped to the current user's role."""
    return PaymentService(db).list_payments(current_user, offset=offset, limit=limit)


# ─── REFUND ENDPOINTS ───────────────────────────────────────────────────


@router.post(
    "/refund",
    response_model=PaymentResponse,
    summary="Refund payment (Admin only)",
    description="Processes a refund for a payment via payload body.",
)
def refund_payment_payload(
    payload: PaymentRefundRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Refund a payment via request body payload (admin only)."""
    return PaymentService(db).refund_payment_payload(current_user, payload)


@router.post(
    "/{payment_id}/refund",
    response_model=PaymentResponse,
    summary="Refund a payment by ID (Admin only)",
    description="**Admin-only.** Processes a refund through Razorpay.",
)
def refund_payment(
    payment_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Refund a payment by ID (admin only)."""
    return PaymentService(db).refund_payment(current_user, payment_id)


# ─── GET INVOICE ────────────────────────────────────────────────────────


@router.get(
    "/invoice/{payment_id}",
    response_model=PaymentInvoiceResponse,
    summary="Get payment invoice",
    description="Returns detailed invoice data for a paid payment.",
)
def get_payment_invoice(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get payment invoice by payment ID."""
    return PaymentService(db).get_payment_invoice(current_user, payment_id)


# ─── GET BY ID ──────────────────────────────────────────────────────────


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    summary="Get payment by ID",
    description="Returns the full details of a single payment by its ID.",
)
def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Retrieve a single payment by its ID."""
    return PaymentService(db).get_payment(current_user, payment_id)


