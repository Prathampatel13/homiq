import os
from typing import List, Optional
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_FROM_EMAIL or "noreply@homiq.com",
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME="HomiQ Services",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

async def send_email_async(
    subject: str,
    email_to: str,
    body: str,
    subtype: MessageType = MessageType.html,
):
    """
    Asynchronously send an email using fastapi-mail.
    """
    # If SMTP is not configured, just log and skip to prevent errors in development
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"SMTP not configured. Skipping email to {email_to}")
        print(f"Subject: {subject}\nBody: {body}")
        return

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype=subtype,
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except Exception as e:
        print(f"Failed to send email to {email_to}: {e}")

import threading
import asyncio

def send_email_in_background(subject: str, email_to: str, body: str):
    """
    Fire and forget email sender for synchronous contexts.
    """
    def run_async():
        asyncio.run(send_email_async(subject, email_to, body))
    threading.Thread(target=run_async, daemon=True).start()

