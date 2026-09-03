from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "HomiQ"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: str = "http://localhost:5173"

    UPLOAD_DIR: str = "uploads/profiles"

    # ── Razorpay ──────────────────────────────────────────────────────
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""

    # ── Cloudinary ────────────────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # ── Google Maps & OAuth ──────────────────────────────────────────
    GOOGLE_MAPS_API_KEY: str = ""
    GOOGLE_CLIENT_ID: str = ""

    # ── Email / SMTP ─────────────────────────────────────────────────
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    FRONTEND_URL: str = "http://localhost:5173"

    # ── Password Recovery ────────────────────────────────────────────
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    PASSWORD_RESET_OTP_EXPIRE_MINUTES: int = 10
    PASSWORD_RESET_OTP_LENGTH: int = 6
    PASSWORD_RESET_OTP_MAX_ATTEMPTS: int = 5
    PASSWORD_RESET_OTP_RESEND_COOLDOWN_SECONDS: int = 60

    # ── SMS ──────────────────────────────────────────────────────────
    SMS_API_KEY: str = ""
    SMS_API_SECRET: str = ""
    SMS_FROM: str = ""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
