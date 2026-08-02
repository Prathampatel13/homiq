"""
SMS integration for sending notifications via SMS gateway.

Provides:
- OTP delivery
- Booking status updates
- Technician arrival notifications
- Payment confirmations
"""

from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class SMSClient:
    """Client for sending SMS notifications."""

    _instance: Optional["SMSClient"] = None

    def __new__(cls) -> "SMSClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.api_key = settings.SMS_API_KEY
        self.api_secret = settings.SMS_API_SECRET
        self.from_number = settings.SMS_FROM

    def _is_configured(self) -> bool:
        """Check if SMS gateway is properly configured."""
        return bool(self.api_key)

    async def send_sms(self, to_phone: str, message: str) -> bool:
        """
        Send an SMS message to a phone number.

        Args:
            to_phone: Recipient phone number (with country code).
            message: SMS text content.

        Returns:
            bool: True if sent successfully, False otherwise.
        """
        if not self._is_configured():
            logger.warning("SMS not configured. SMS not sent to %s", to_phone)
            return False

        try:
            # Using a generic HTTP-based SMS gateway pattern
            # Replace with actual SMS provider (Twilio, MSG91, etc.)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sms-provider.com/v1/send",  # Replace with actual endpoint
                    json={
                        "api_key": self.api_key,
                        "api_secret": self.api_secret,
                        "from": self.from_number,
                        "to": to_phone,
                        "text": message,
                    },
                    timeout=10.0,
                )

                if response.is_success:
                    logger.info("SMS sent successfully to %s", to_phone)
                    return True
                else:
                    logger.error(
                        "SMS provider returned error %s: %s",
                        response.status_code,
                        response.text,
                    )
                    return False

        except httpx.RequestError as exc:
            logger.error("SMS request failed for %s: %s", to_phone, exc)
            return False
        except Exception as exc:
            logger.error("Unexpected error sending SMS to %s: %s", to_phone, exc)
            return False

    async def send_otp(self, to_phone: str, otp: str) -> bool:
        """Send OTP verification code."""
        message = f"Your HomiQ verification code is: {otp}. Valid for 10 minutes."
        return await self.send_sms(to_phone, message)

    async def send_booking_confirmation(self, to_phone: str, booking_number: str) -> bool:
        """Send booking confirmation SMS."""
        message = f"Your HomiQ booking {booking_number} has been confirmed. We'll notify you when a technician is assigned."
        return await self.send_sms(to_phone, message)

    async def send_technician_assigned(self, to_phone: str, booking_number: str, technician_name: str) -> bool:
        """Send technician assignment notification."""
        message = f"Technician {technician_name} has been assigned to your booking {booking_number}."
        return await self.send_sms(to_phone, message)

    async def send_technician_arriving(self, to_phone: str, booking_number: str, eta_minutes: int) -> bool:
        """Send technician arrival notification."""
        message = f"Your technician is arriving in approximately {eta_minutes} minutes for booking {booking_number}."
        return await self.send_sms(to_phone, message)

    async def send_payment_success(self, to_phone: str, booking_number: str, amount: float) -> bool:
        """Send payment success notification."""
        message = f"Payment of ₹{amount:.2f} for booking {booking_number} was successful. Thank you for choosing HomiQ!"
        return await self.send_sms(to_phone, message)

    async def send_review_reminder(self, to_phone: str, booking_number: str) -> bool:
        """Send review reminder."""
        message = f"Your service for booking {booking_number} is complete. We'd love to hear your feedback! Rate your experience on HomiQ."
        return await self.send_sms(to_phone, message)

