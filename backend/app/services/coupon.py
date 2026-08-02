from __future__ import annotations

from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.coupon import CouponCRUD
from app.crud.booking import BookingCRUD
from app.models.auth import User
from app.schemas.coupons import (
    CouponCreate,
    CouponListResponse,
    CouponResponse,
    CouponUpdate,
    CouponValidateRequest,
    CouponValidateResponse,
)


class CouponService:
    """Service layer for coupon operations."""

    def __init__(self, db: Session):
        self.db = db
        self.crud = CouponCRUD(db)

    # ── Create ─────────────────────────────────────────────────────────

    def create_coupon(self, current_user: User, payload: CouponCreate) -> CouponResponse:
        """Create a new coupon. Admin only."""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required.",
            )

        # Check for duplicate code
        existing = self.crud.get_by_code(payload.code.upper())
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coupon code already exists.",
            )

        data = payload.model_dump()
        data["code"] = data["code"].upper()
        data["created_by"] = current_user.id
        coupon = self.crud.create(data)
        return CouponResponse.model_validate(coupon)

    # ── Get ────────────────────────────────────────────────────────────

    def get_coupon(self, coupon_id: int) -> CouponResponse:
        """Get a coupon by ID."""
        coupon = self.crud.get(coupon_id)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coupon not found.",
            )
        return CouponResponse.model_validate(coupon)

    def get_coupon_by_code(self, code: str) -> CouponResponse:
        """Get a coupon by code."""
        coupon = self.crud.get_by_code(code.upper())
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coupon not found.",
            )
        return CouponResponse.model_validate(coupon)

    # ── List ───────────────────────────────────────────────────────────

    def list_coupons(
        self,
        is_active: Optional[bool] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> CouponListResponse:
        """List coupons with optional active filter."""
        coupons = self.crud.list_coupons(
            is_active=is_active,
            offset=offset,
            limit=limit,
        )
        total = self.crud.count_coupons(is_active=is_active)
        return CouponListResponse(
            items=[CouponResponse.model_validate(c) for c in coupons],
            total=total,
        )

    # ── Update ─────────────────────────────────────────────────────────

    def update_coupon(
        self, current_user: User, coupon_id: int, payload: CouponUpdate
    ) -> CouponResponse:
        """Update a coupon. Admin only."""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required.",
            )

        coupon = self.crud.get(coupon_id)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coupon not found.",
            )

        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update.",
            )

        if "code" in data:
            data["code"] = data["code"].upper()

        updated = self.crud.update(coupon_id, data)
        return CouponResponse.model_validate(updated)

    # ── Delete ─────────────────────────────────────────────────────────

    def delete_coupon(self, current_user: User, coupon_id: int) -> dict[str, str]:
        """Delete a coupon. Admin only."""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required.",
            )

        deleted = self.crud.delete(coupon_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coupon not found.",
            )
        return {"message": "Coupon deleted successfully."}

    # ── Validate ───────────────────────────────────────────────────────

    def validate_coupon(
        self, current_user: User, payload: CouponValidateRequest
    ) -> CouponValidateResponse:
        """
        Validate a coupon code for a booking.

        Checks:
        - Coupon exists and is active
        - Coupon is within validity period
        - Minimum order value met
        - Usage limits not exceeded
        - Applicable services match
        - Per-user limit not exceeded
        """
        # Get booking to verify ownership and amount
        booking_crud = BookingCRUD(self.db)
        booking = booking_crud.get_booking(payload.booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        # Verify booking ownership
        from app.crud.customer import CustomerCRUD
        customer = CustomerCRUD(self.db).get_by_user_id(current_user.id)
        if not customer or booking.customer_id != customer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This booking does not belong to you.",
            )

        amount = booking.final_price or booking.estimated_price or 0
        service_id = booking.service_id

        is_valid, message, coupon = self.crud.validate_coupon(
            code=payload.code.upper(),
            user_id=current_user.id,
            booking_amount=amount,
            service_id=service_id,
        )

        if not is_valid or not coupon:
            return CouponValidateResponse(
                valid=False,
                message=message,
                discount_amount=0.0,
            )

        # Calculate discount
        discount_amount = self._calculate_discount(coupon, amount)

        return CouponValidateResponse(
            valid=True,
            coupon=CouponResponse.model_validate(coupon),
            discount_amount=discount_amount,
            message=f"Coupon applied! You save ₹{discount_amount:.2f}",
        )

    def _calculate_discount(self, coupon: Any, amount: float) -> float:
        """Calculate the discount amount based on coupon rules."""
        if coupon.discount_type == "percentage":
            discount = amount * (coupon.discount_value / 100.0)
            if coupon.max_discount:
                discount = min(discount, coupon.max_discount)
        else:
            discount = coupon.discount_value

        return round(min(discount, amount), 2)

    def apply_coupon(
        self,
        current_user: User,
        coupon_code: str,
        booking_id: int,
    ) -> dict[str, Any]:
        """
        Apply a coupon to a booking and record usage.

        This is called after successful validation to persist the usage.
        """
        # Validate first
        validation = self.validate_coupon(
            current_user,
            CouponValidateRequest(code=coupon_code, booking_id=booking_id),
        )

        if not validation.valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation.message,
            )

        # Record usage
        self.crud.record_usage(
            coupon_id=validation.coupon.id,
            user_id=current_user.id,
            booking_id=booking_id,
            discount_amount=validation.discount_amount,
        )

        return {
            "coupon_code": coupon_code,
            "discount_amount": validation.discount_amount,
            "message": validation.message,
        }

