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


def send_password_reset_link_email(email_to: str, user_name: str, token: str):
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #4CAF50;">Reset your HomiQ password</h2>
        <p>Hi {user_name},</p>
        <p>You requested a password reset. Click the button below to set a new password:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" style="background-color: #4CAF50; color: white; padding: 14px 25px; text-align: center; text-decoration: none; display: inline-block; border-radius: 4px; font-weight: bold;">Reset Password</a>
        </div>
        <p>This reset link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
        <p style="color: #888; font-size: 12px; margin-top: 40px;">If you did not request this, you can safely ignore this email.</p>
    </div>
    """
    send_email_in_background(
        subject="Reset your HomiQ password",
        email_to=email_to,
        body=html_body
    )


def send_password_reset_otp_email(email_to: str, user_name: str, otp: str):
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; text-align: center;">
        <h2 style="color: #4CAF50;">Your HomiQ password reset OTP</h2>
        <p>Hi {user_name},</p>
        <p>Use the following 6-digit code to reset your password:</p>
        <div style="background-color: #f4f4f4; padding: 20px; border-radius: 8px; margin: 20px auto; max-width: 200px;">
            <h1 style="margin: 0; letter-spacing: 5px; color: #333;">{otp}</h1>
        </div>
        <p>This OTP expires in {settings.PASSWORD_RESET_OTP_EXPIRE_MINUTES} minutes.</p>
        <p style="color: #888; font-size: 12px; margin-top: 40px;">If you did not request this, you can ignore this email.</p>
    </div>
    """
    send_email_in_background(
        subject="Your HomiQ password reset OTP",
        email_to=email_to,
        body=html_body
    )

