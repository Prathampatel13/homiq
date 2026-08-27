"""
Razorpay payment gateway integration.

Provides a clean wrapper around the Razorpay Python SDK for:
- Creating orders
- Verifying payments
- Processing refunds
- Fetching payment details
"""

from __future__ import annotations

from typing import Any, Optional

import razorpay
from fastapi import HTTPException, status

from app.core.config import settings


class RazorpayClient:
    """Singleton-style Razorpay client wrapper."""

    _instance: Optional["RazorpayClient"] = None
    _client: Optional[razorpay.Client] = None

    def __new__(cls) -> "RazorpayClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def client(self) -> razorpay.Client:
        """Lazy-initialised Razorpay client."""
        if self._client is None:
            if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Razorpay is not configured. Please contact support.",
                )
            self._client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
        return self._client

    def create_order(
        self,
        amount_paise: int,
        currency: str = "INR",
        receipt: Optional[str] = None,
        notes: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Create a Razorpay order.

        Args:
            amount_paise: Amount in the smallest currency unit (paise for INR).
            currency: Three-letter ISO currency code (default: INR).
            receipt: Optional receipt identifier.
            notes: Optional key-value notes (max 15 keys).

        Returns:
            dict: Razorpay order response with id, amount, currency, status, etc.

        Raises:
            HTTPException: If order creation fails.
        """
        try:
            data: dict[str, Any] = {
                "amount": amount_paise,
                "currency": currency,
            }
            if receipt:
                data["receipt"] = receipt
            if notes:
                data["notes"] = notes

            return self.client.order.create(data=data)
        except razorpay.errors.BadRequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Razorpay bad request: {exc}",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Razorpay order creation failed: {exc}",
            )

    def verify_payment(
        self,
        order_id: str,
        payment_id: str,
        signature: str,
    ) -> bool:
        """
        Verify a Razorpay payment signature.

        Args:
            order_id: Razorpay order ID.
            payment_id: Razorpay payment ID.
            signature: Razorpay signature from the frontend callback.

        Returns:
            bool: True if the signature is valid.
        """
        import hashlib
        import hmac

        expected = hmac.new(
            key=settings.RAZORPAY_KEY_SECRET.encode(),
            msg=f"{order_id}|{payment_id}".encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def fetch_payment(self, payment_id: str) -> dict[str, Any]:
        """
        Fetch payment details from Razorpay.

        Args:
            payment_id: Razorpay payment ID.

        Returns:
            dict: Payment details including method, status, amount, etc.
        """
        try:
            return self.client.payment.fetch(payment_id)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch payment details: {exc}",
            )

    def process_refund(
        self,
        payment_id: str,
        amount_paise: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Process a refund for a payment.

        Args:
            payment_id: Razorpay payment ID.
            amount_paise: Amount to refund (in paise). If None, full refund.

        Returns:
            dict: Refund response from Razorpay.
        """
        try:
            if amount_paise:
                return self.client.payment.refund(payment_id, amount_paise)
            return self.client.payment.refund(payment_id)
        except razorpay.errors.BadRequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Refund failed: {exc}",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Razorpay refund failed: {exc}",
            )

    def fetch_all_payments(
        self,
        from_date: Optional[int] = None,
        to_date: Optional[int] = None,
        count: int = 10,
        skip: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Fetch all payments with optional date filtering.

        Args:
            from_date: Unix timestamp for start date.
            to_date: Unix timestamp for end date.
            count: Number of payments to fetch (max 100).
            skip: Number of payments to skip.

        Returns:
            list[dict]: List of payment records.
        """
        try:
            filters: dict[str, Any] = {"count": count, "skip": skip}
            if from_date:
                filters["from"] = from_date
            if to_date:
                filters["to"] = to_date
            return self.client.payment.all(filters)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch payments: {exc}",
            )

    def create_customer(
        self,
        name: str,
        email: str,
        contact: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Create a customer in Razorpay.

        Args:
            name: Customer's full name.
            email: Customer's email address.
            contact: Customer's phone number (optional).

        Returns:
            dict: Created customer details.
        """
        try:
            data: dict[str, Any] = {
                "name": name,
                "email": email,
            }
            if contact:
                data["contact"] = contact
            return self.client.customer.create(data=data)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create Razorpay customer: {exc}",
            )

