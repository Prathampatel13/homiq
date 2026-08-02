
"""
Payment management endpoints.

All endpoints are JWT-protected and require a valid Bearer token.
- Customers can create orders, verify payments, and list own payments.
- Admins can list all payments, view any payment, and process refunds.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user, get_current_admin
from app.schemas.payments import (
    PaymentCreateOrder,
    PaymentListResponse,
    PaymentResponse,
    PaymentVerify,
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
    """Create a Razorpay order for a booking.

    Args:
        payload: Booking ID for which to create the order.
        current_user: Authenticated user (JWT-protected, must be a customer).
        db: Database session.

    Returns:
        dict: Razorpay order details including order_id, amount, currency, key_id.

    Raises:
        401: If not authenticated.
        404: If the customer profile or booking is not found.
        400: If the booking has no final price or a payment already exists.
    """
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
    """Verify a Razorpay payment signature.

    Args:
        payload: Razorpay order_id, payment_id, and signature.
        current_user: Authenticated user (JWT-protected).
        db: Database session.

    Returns:
        PaymentResponse: The updated payment record.

    Raises:
        401: If not authenticated.
        404: If the payment order is not found.
        400: If the signature is invalid or payment already processed.
    """
    return PaymentService(db).verify_payment(payload)


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
    """List payments with pagination, scoped to the current user's role.

    Args:
        offset: Number of records to skip (default 0).
        limit: Maximum number of records to return (default 100).
        current_user: Authenticated user (JWT-protected).
        db: Database session.

    Returns:
        PaymentListResponse: A list of payments and the total count.

    Raises:
        401: If not authenticated.
    """
    return PaymentService(db).list_payments(current_user, offset=offset, limit=limit)


# ─── GET BY ID ──────────────────────────────────────────────────────────


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    summary="Get payment by ID",
    description=(
        "Returns the full details of a single payment by its ID. "
        "Access is restricted to the payment owner (customer) or an admin."
    ),
    response_description="The requested payment details.",
)
def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Retrieve a single payment by its ID.

    Args:
        payment_id: The unique payment ID.
        current_user: Authenticated user (JWT-protected).
        db: Database session.

    Returns:
        PaymentResponse: The payment details.

    Raises:
        401: If not authenticated.
        403: If not authorized to view this payment.
        404: If the payment is not found.
    """
    return PaymentService(db).get_payment(current_user, payment_id)


# ─── REFUND (Admin only) ────────────────────────────────────────────────


@router.post(
    "/{payment_id}/refund",
    response_model=PaymentResponse,
    summary="Refund a payment (Admin only)",
    description=(
        "**Admin-only.** Processes a refund through Razorpay and updates "
        "the payment status to 'refunded'. The associated booking's "
        "payment_status is also updated."
    ),
    response_description="The updated payment record with status 'refunded'.",
)
def refund_payment(
    payment_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Any:
    """Refund a payment (admin only).

    Args:
        payment_id: The unique payment ID.
        current_user: Authenticated user (JWT-protected, must be admin).
        db: Database session.

    Returns:
        PaymentResponse: The updated payment with status 'refunded'.

    Raises:
        401: If not authenticated.
        403: If not an admin.
        404: If the payment is not found.
        400: If the payment is not in 'paid' status.
    """
    return PaymentService(db).refund_payment(current_user, payment_id)

