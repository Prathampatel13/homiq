from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.coupons import Coupon, CouponUsage


class CouponCRUD:
    def __init__(self, db: Session):
        self.db = db

    # ── Create ─────────────────────────────────────────────────────────

    def create(self, data: dict) -> Coupon:
        coupon = Coupon(**data)
        self.db.add(coupon)
        self.db.commit()
        self.db.refresh(coupon)
        return coupon

    # ── Get ────────────────────────────────────────────────────────────

    def get(self, coupon_id: int) -> Optional[Coupon]:
        return self.db.get(Coupon, coupon_id)

    def get_by_code(self, code: str) -> Optional[Coupon]:
        stmt = select(Coupon).where(Coupon.code == code)
        return self.db.scalar(stmt)

    # ── List ───────────────────────────────────────────────────────────

    def list_coupons(
        self,
        is_active: Optional[bool] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Coupon]:
        stmt = select(Coupon).order_by(Coupon.created_at.desc())
        if is_active is not None:
            stmt = stmt.where(Coupon.is_active.is_(is_active))
        stmt = stmt.offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_coupons(self, is_active: Optional[bool] = None) -> int:
        stmt = select(func.count(Coupon.id))
        if is_active is not None:
            stmt = stmt.where(Coupon.is_active.is_(is_active))
        return self.db.scalar(stmt) or 0

    # ── Update ─────────────────────────────────────────────────────────

    def update(self, coupon_id: int, data: dict) -> Optional[Coupon]:
        coupon = self.get(coupon_id)
        if not coupon:
            return None
        for key, value in data.items():
            setattr(coupon, key, value)
        self.db.commit()
        self.db.refresh(coupon)
        return coupon

    # ── Delete ─────────────────────────────────────────────────────────

    def delete(self, coupon_id: int) -> bool:
        coupon = self.get(coupon_id)
        if not coupon:
            return False
        self.db.delete(coupon)
        self.db.commit()
        return True

    # ── Validation ─────────────────────────────────────────────────────

    def validate_coupon(self, code: str, user_id: int, booking_amount: float, service_id: int) -> tuple[bool, str, Optional[Coupon]]:
        """
        Validate a coupon code for a given user, amount, and service.

        Returns:
            tuple[bool, str, Optional[Coupon]]: (is_valid, message, coupon)
        """
        coupon = self.get_by_code(code)
        if not coupon:
            return False, "Invalid coupon code", None

        if not coupon.is_active:
            return False, "Coupon is no longer active", None

        today = date.today()
        if today < coupon.valid_from:
            return False, "Coupon is not yet valid", None
        if today > coupon.valid_until:
            return False, "Coupon has expired", None

        if coupon.min_order_value and booking_amount < coupon.min_order_value:
            return False, f"Minimum order value of ₹{coupon.min_order_value:.2f} required", None

        if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
            return False, "Coupon usage limit has been reached", None

        # Check per-user limit
        user_usage_count = self.db.scalar(
            select(func.count(CouponUsage.id)).where(
                CouponUsage.coupon_id == coupon.id,
                CouponUsage.user_id == user_id,
            )
        ) or 0
        if user_usage_count >= coupon.per_user_limit:
            return False, "You have already used this coupon the maximum number of times", None

        # Check if applicable_services is set and service is allowed
        if coupon.applicable_services:
            import json
            try:
                applicable_ids = json.loads(coupon.applicable_services)
                if applicable_ids and service_id not in applicable_ids:
                    return False, "Coupon is not applicable for this service", None
            except (json.JSONDecodeError, TypeError):
                pass

        return True, "Coupon is valid", coupon

    # ── Usage Tracking ─────────────────────────────────────────────────

    def record_usage(self, coupon_id: int, user_id: int, booking_id: int, discount_amount: float) -> CouponUsage:
        """Record coupon usage for a booking."""
        usage = CouponUsage(
            coupon_id=coupon_id,
            user_id=user_id,
            booking_id=booking_id,
            discount_amount=discount_amount,
        )
        self.db.add(usage)

        # Increment usage count
        stmt = (
            update(Coupon)
            .where(Coupon.id == coupon_id)
            .values(usage_count=Coupon.usage_count + 1)
        )
        self.db.execute(stmt)
        self.db.commit()
        self.db.refresh(usage)
        return usage

    def get_user_usage_count(self, coupon_id: int, user_id: int) -> int:
        return self.db.scalar(
            select(func.count(CouponUsage.id)).where(
                CouponUsage.coupon_id == coupon_id,
                CouponUsage.user_id == user_id,
            )
        ) or 0

