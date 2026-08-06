from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.payments import Payment, PaymentStatus


class PaymentCRUD:
    def __init__(self, db: Session):
        self.db = db

    # -----------------------------------
    # Create
    # -----------------------------------

    def create(self, data: dict) -> Payment:
        payment = Payment(**data)

        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)

        return payment

    # -----------------------------------
    # Get
    # -----------------------------------

    def get(self, payment_id: int) -> Optional[Payment]:
        return self.db.get(Payment, payment_id)

    def get_by_booking(self, booking_id: int) -> Optional[Payment]:
        stmt = (
            select(Payment)
            .where(Payment.booking_id == booking_id)
        )

        return self.db.scalar(stmt)

    def get_by_order_id(
        self,
        order_id: str,
    ) -> Optional[Payment]:

        stmt = (
            select(Payment)
            .where(Payment.razorpay_order_id == order_id)
        )

        return self.db.scalar(stmt)

    def get_by_payment_id(
        self,
        payment_id: str,
    ) -> Optional[Payment]:

        stmt = (
            select(Payment)
            .where(Payment.razorpay_payment_id == payment_id)
        )

        return self.db.scalar(stmt)

    # -----------------------------------
    # List
    # -----------------------------------

    def list_customer_payments(
        self,
        customer_id: int,
        offset: int = 0,
        limit: int = 100,
    ):

        stmt = (
            select(Payment)
            .where(Payment.customer_id == customer_id)
            .order_by(Payment.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return self.db.execute(stmt).scalars().all()

    def count_customer_payments(
        self,
        customer_id: int,
    ) -> int:

        return (
            self.db.scalar(
                select(func.count(Payment.id))
                .where(Payment.customer_id == customer_id)
            )
            or 0
        )

    # -----------------------------------
    # Update
    # -----------------------------------

    def update(
        self,
        payment_id: int,
        data: dict,
    ) -> Optional[Payment]:

        payment = self.get(payment_id)

        if not payment:
            return None

        for key, value in data.items():
            setattr(payment, key, value)

        self.db.commit()
        self.db.refresh(payment)

        return payment

    # -----------------------------------
    # Status
    # -----------------------------------

    def mark_paid(
        self,
        payment: Payment,
        razorpay_payment_id: str,
        razorpay_signature: str,
        payment_method,
    ) -> Payment:

        payment.status = PaymentStatus.PAID
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.payment_method = payment_method

        self.db.commit()
        self.db.refresh(payment)

        return payment

    def mark_failed(
        self,
        payment: Payment,
    ) -> Payment:

        payment.status = PaymentStatus.FAILED

        self.db.commit()
        self.db.refresh(payment)

        return payment

    def mark_refunded(
        self,
        payment: Payment,
    ) -> Payment:

        payment.status = PaymentStatus.REFUNDED

        self.db.commit()
        self.db.refresh(payment)

        return payment

    # -----------------------------------
    # Payment History
    # -----------------------------------

    def get_payment_history(
        self,
        customer_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Payment]:
        """Fetch payment transaction history."""
        stmt = select(Payment)
        if customer_id is not None:
            stmt = stmt.where(Payment.customer_id == customer_id)
        stmt = stmt.order_by(Payment.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_payment_history(self, customer_id: Optional[int] = None) -> int:
        """Count total payment records for history pagination."""
        stmt = select(func.count(Payment.id))
        if customer_id is not None:
            stmt = stmt.where(Payment.customer_id == customer_id)
        return self.db.scalar(stmt) or 0