"""
Coupon management endpoints.

Admin: Full CRUD for coupons.
Customers: Validate and apply coupons.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user
from app.schemas.coupons import (
    CouponCreate,
    CouponListResponse,
    CouponResponse,
    CouponUpdate,
    CouponValidateRequest,
    CouponValidateResponse,
)
from app.services.coupon import CouponService

router = APIRouter(prefix="/coupons", tags=["Coupons"])


@router.post(
    "/",
    response_model=CouponResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a coupon (Admin)",
    description="**Admin only.** Creates a new coupon with discount rules, validity dates, and usage limits.",
)
def create_coupon(
    payload: CouponCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create a new coupon. Admin access required."""
    return CouponService(db).create_coupon(current_user, payload)


@router.get(
    "/",
    response_model=CouponListResponse,
    summary="List coupons (Admin)",
    description="**Admin only.** Returns a paginated list of all coupons, with optional active filter.",
)
def list_coupons(
    is_active: Optional[bool] = None,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """List coupons with optional active filter. Admin access required."""
    return CouponService(db).list_coupons(
        is_active=is_active,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{coupon_id}",
    response_model=CouponResponse,
    summary="Get coupon by ID",
    description="Returns the details of a specific coupon by its ID.",
)
def get_coupon(
    coupon_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get a coupon by its ID."""
    return CouponService(db).get_coupon(coupon_id)


@router.get(
    "/code/{code}",
    response_model=CouponResponse,
    summary="Get coupon by code",
    description="Returns coupon details by its unique code.",
)
def get_coupon_by_code(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get a coupon by its code."""
    return CouponService(db).get_coupon_by_code(code)


@router.put(
    "/{coupon_id}",
    response_model=CouponResponse,
    summary="Update a coupon (Admin)",
    description="**Admin only.** Updates one or more fields of an existing coupon.",
)
def update_coupon(
    coupon_id: int,
    payload: CouponUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Update a coupon by ID. Admin access required."""
    return CouponService(db).update_coupon(current_user, coupon_id, payload)


@router.delete(
    "/{coupon_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a coupon (Admin)",
    description="**Admin only.** Deletes a coupon by its ID.",
)
def delete_coupon(
    coupon_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Delete a coupon by ID. Admin access required."""
    return CouponService(db).delete_coupon(current_user, coupon_id)


# ── Customer Endpoints ─────────────────────────────────────────────────


@router.post(
    "/validate",
    response_model=CouponValidateResponse,
    summary="Validate a coupon",
    description="Validates a coupon code against a booking. Checks all rules including expiry, usage limits, minimum order value, and service applicability.",
)
def validate_coupon(
    payload: CouponValidateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Validate a coupon code for a booking."""
    return CouponService(db).validate_coupon(current_user, payload)


@router.post(
    "/apply",
    summary="Apply a coupon to booking",
    description="Validates and applies a coupon to a booking. Records the usage and returns the discount amount.",
)
def apply_coupon(
    payload: CouponValidateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Apply a validated coupon to a booking."""
    return CouponService(db).apply_coupon(
        current_user,
        payload.code,
        payload.booking_id,
    )

