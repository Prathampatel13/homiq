"""
Email integration for transactional and notification emails.

Provides:
- SMTP-based email sending
- HTML template rendering
- Booking confirmation, payment receipt, OTP, and notification emails
"""

from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Optional

from app.core.config import BASE_DIR, settings

logger = logging.getLogger(__name__)


class EmailClient:
    """Client for sending transactional emails via SMTP."""

    _instance: Optional["EmailClient"] = None
    TEMPLATES_DIR = BASE_DIR / "templates" / "emails"

    def __new__(cls) -> "EmailClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL

    def _is_configured(self) -> bool:
        """Check if SMTP is properly configured."""
        return bool(self.host and self.user and self.password)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email via SMTP.

        Args:
            to_email: Recipient email address.
            subject: Email subject line.
            html_content: HTML body content.
            text_content: Plain text fallback (optional).

        Returns:
            bool: True if sent successfully, False otherwise.
        """
        if not self._is_configured():
            logger.warning("SMTP not configured. Email not sent to %s", to_email)
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject

            # Attach plain text fallback
            if text_content:
                msg.attach(MIMEText(text_content, "plain"))

            # Attach HTML content
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)

            logger.info("Email sent successfully to %s: %s", to_email, subject)
            return True
        except smtplib.SMTPException as exc:
            logger.error("SMTP error sending email to %s: %s", to_email, exc)
            return False
        except Exception as exc:
            logger.error("Failed to send email to %s: %s", to_email, exc)
            return False

    def _render_template(self, template_name: str, context: dict[str, Any]) -> str:
        """
        Render an HTML email template with context variables.

        Args:
            template_name: Name of the template file (e.g., 'booking_confirmation.html').
            context: Dictionary of variables to substitute.

        Returns:
            str: Rendered HTML content.
        """
        template_path = self.TEMPLATES_DIR / template_name
        if not template_path.exists():
            logger.warning("Email template not found: %s", template_path)
            return "<html><body><p>Email content unavailable.</p></body></html>"

        html = template_path.read_text(encoding="utf-8")
        for key, value in context.items():
            html = html.replace(f"{{{{ {key} }}}}", str(value))
        return html

    async def send_booking_confirmation(
        self,
        to_email: str,
        customer_name: str,
        booking_number: str,
        service_name: str,
        booking_date: str,
        amount: float,
    ) -> bool:
        """Send booking confirmation email."""
        subject = f"Booking Confirmed - {booking_number}"
        html = self._render_template("booking_confirmation.html", {
            "customer_name": customer_name,
            "booking_number": booking_number,
            "service_name": service_name,
            "booking_date": booking_date,
            "amount": f"₹{amount:.2f}",
        })
        return await self.send_email(to_email, subject, html)

    async def send_payment_receipt(
        self,
        to_email: str,
        customer_name: str,
        booking_number: str,
        amount: float,
        payment_id: str,
        payment_method: str,
    ) -> bool:
        """Send payment receipt email."""
        subject = f"Payment Receipt - {booking_number}"
        html = self._render_template("payment_receipt.html", {
            "customer_name": customer_name,
            "booking_number": booking_number,
            "amount": f"₹{amount:.2f}",
            "payment_id": payment_id,
            "payment_method": payment_method,
        })
        return await self.send_email(to_email, subject, html)

    async def send_otp(
        self,
        to_email: str,
        customer_name: str,
        otp: str,
        booking_number: str,
    ) -> bool:
        """Send OTP for service completion verification."""
        subject = f"Your OTP for Booking {booking_number}"
        html = self._render_template("otp_email.html", {
            "customer_name": customer_name,
            "otp": otp,
            "booking_number": booking_number,
        })
        return await self.send_email(to_email, subject, html)

    async def send_technician_assigned(
        self,
        to_email: str,
        customer_name: str,
        technician_name: str,
        booking_number: str,
    ) -> bool:
        """Send notification when a technician is assigned."""
        subject = f"Technician Assigned - {booking_number}"
        html = self._render_template("technician_assigned.html", {
            "customer_name": customer_name,
            "technician_name": technician_name,
            "booking_number": booking_number,
        })
        return await self.send_email(to_email, subject, html)

    async def send_review_reminder(
        self,
        to_email: str,
        customer_name: str,
        booking_number: str,
        review_link: str,
    ) -> bool:
        """Send review reminder after service completion."""
        subject = f"How was your service? Review Booking {booking_number}"
        html = self._render_template("review_reminder.html", {
            "customer_name": customer_name,
            "booking_number": booking_number,
            "review_link": review_link,
        })
        return await self.send_email(to_email, subject, html)

