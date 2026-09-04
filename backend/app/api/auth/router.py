from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user import UserCRUD
from app.database.session import get_db
from app.models.auth import User
from app.schemas.auth import ForgotPasswordRequest, LoginRequest, RegisterRequest, ResetPasswordRequest, Token, RefreshRequest
from app.security.deps import get_current_user
from app.security.passwords import hash_password
from app.security.tokens import create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> Token:
    crud = UserCRUD(db)
    existing = crud.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        user = crud.create_user(
            email=str(payload.email),
            password=payload.password,
            full_name=payload.full_name,
            phone=payload.phone,
            role_name=payload.role,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    tokens = crud.create_tokens(user)
    tokens["user"] = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": f"ROLE_{user.role.name.upper()}" if user.role else "ROLE_CUSTOMER",
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }
    return Token(**tokens)


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    crud = UserCRUD(db)
    user = crud.authenticate(identifier=payload.identifier, password=payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    tokens = crud.create_tokens(user)
    tokens["user"] = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": f"ROLE_{user.role.name.upper()}" if user.role else "ROLE_CUSTOMER",
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }
    return Token(**tokens)


@router.post("/refresh", response_model=Token)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)) -> Token:
    crud = UserCRUD(db)
    record = crud.get_refresh_token(payload.refresh_token)
    if not record:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = crud.get_user_by_id(record.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    tokens = crud.create_tokens(user)
    return Token(**tokens)



from datetime import datetime, timedelta, timezone
import secrets
from jose import jwt

from app.core.config import settings
from app.services.email import send_password_reset_link_email, send_password_reset_otp_email
from app.schemas.auth import SendResetOtpRequest, VerifyResetOtpRequest, VerifyResetOtpResponse, ResetPasswordWithOtpRequest
from app.security.passwords import generate_secure_otp, hash_password, verify_password, validate_password_strength


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    # Rate limit check should go here in a production setup (if implemented as middleware/dependency, else manually)
    
    crud = UserCRUD(db)
    user = crud.get_user_by_email(payload.email)
    if user:
        # Generate secure random token
        raw_token = secrets.token_urlsafe(32)
        token_hash = hash_password(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
        
        crud.create_password_reset_token(user.id, token_hash, expires_at)
        
        full_token = f"{user.id}:{raw_token}"
        send_password_reset_link_email(user.email, user.full_name, full_token)
        
    # Always return success to prevent enumeration
    return {"message": "If an account with that email exists, password reset instructions have been sent."}


@router.post("/send-reset-otp")
def send_reset_otp(payload: SendResetOtpRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    crud = UserCRUD(db)
    user = crud.get_user_by_email(payload.email)
    
    if user:
        # Check cooldown (if last OTP sent within cooldown, we should silently ignore or allow depending on rate limits, 
        # but to prevent enumeration, we just silently succeed or if we want to be strict, we'd have a rate limiter)
        
        raw_otp = generate_secure_otp(settings.PASSWORD_RESET_OTP_LENGTH)
        otp_hash = hash_password(raw_otp)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_OTP_EXPIRE_MINUTES)
        
        crud.create_password_reset_otp(user.id, otp_hash, expires_at)
        send_password_reset_otp_email(user.email, user.full_name, raw_otp)
        
    return {"message": "If an account with that email exists, an OTP has been sent."}


@router.post("/verify-reset-otp", response_model=VerifyResetOtpResponse)
def verify_reset_otp(payload: VerifyResetOtpRequest, db: Session = Depends(get_db)) -> VerifyResetOtpResponse:
    crud = UserCRUD(db)
    user = crud.get_user_by_email(payload.email)
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid OTP or expired.")
        
    active_otp = crud.get_active_password_reset_otp(user.id)
    if not active_otp:
        raise HTTPException(status_code=400, detail="Invalid OTP or expired.")
        
    if active_otp.attempt_count >= settings.PASSWORD_RESET_OTP_MAX_ATTEMPTS:
        raise HTTPException(status_code=400, detail="Too many invalid attempts. Please request a new OTP.")
        
    if not verify_password(payload.otp, active_otp.otp_hash):
        crud.increment_otp_attempt(active_otp.id)
        raise HTTPException(status_code=400, detail="Invalid OTP or expired.")
        
    crud.mark_otp_used(active_otp.id)
    
    # Issue a short-lived token to authorize the password reset operation
    expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    reset_auth_token = jwt.encode(
        {"sub": str(user.id), "type": "otp_reset_auth", "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return VerifyResetOtpResponse(reset_token=reset_auth_token)


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    crud = UserCRUD(db)
    user = None
    
    # Validate password strength
    is_valid, msg = validate_password_strength(payload.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    # 1. Check if token is a valid reset link token (DB hash)
    # Since we can't search by raw token, we must decode it if it was a JWT, but now it's a raw secrets token.
    # Wait, the frontend sends raw_token in payload.token.
    # We don't have user_id, so we'd have to find the token in DB.
    # Wait, token_hash = hash_password(token) uses a random salt. We can't do a DB lookup by token!
    # Ah! bcrypt hash cannot be searched in the DB because of the random salt.
    # If the token is raw URL-safe string, we must either:
    # A) include the user_id in the token: f"{user.id}:{raw_token}"
    # B) use a deterministic hash like SHA256 for the token storage so we can do a DB lookup.
    
    # Let's check if it's an OTP authorized JWT token
    if payload.token:
        try:
            # First try parsing as JWT (OTP auth token)
            payload_data = jwt.decode(payload.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload_data.get("type") == "otp_reset_auth":
                user_id = int(payload_data.get("sub"))
                user = crud.get_user_by_id(user_id)
        except Exception:
            pass
            
        if not user:
            # Try finding the reset link token. Since it was hashed with bcrypt, this is problematic.
            # Let's fix this in a moment: reset link token needs to be `user_id:raw_token` format.
            if ":" in payload.token:
                user_id_str, raw_token = payload.token.split(":", 1)
                try:
                    user_id = int(user_id_str)
                    user = crud.get_user_by_id(user_id)
                    if user:
                        # Find tokens for user
                        from sqlalchemy import select
                        from app.models.auth import PasswordResetToken
                        tokens = db.scalars(select(PasswordResetToken).where(
                            PasswordResetToken.user_id == user_id,
                            PasswordResetToken.used_at.is_(None),
                            PasswordResetToken.expires_at > datetime.now(timezone.utc)
                        )).all()
                        
                        valid_token_record = None
                        for t in tokens:
                            if verify_password(raw_token, t.token_hash):
                                valid_token_record = t
                                break
                        
                        if valid_token_record:
                            crud.mark_password_reset_token_used(valid_token_record.id)
                        else:
                            user = None
                except ValueError:
                    pass

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
        
    crud.update_password(user.id, payload.new_password)
    
    return {"message": "Password successfully updated"}



@router.get("/me")
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "role": f"ROLE_{current_user.role.name.upper()}" if current_user.role else "ROLE_CUSTOMER",
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "avatar_url": current_user.avatar_url,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }


# ─── USER AVATAR & PROFILE ENDPOINTS (/users/me) ─────────────────────────

from fastapi import File, UploadFile
from app.schemas.media import StandardMediaResponse
from app.services.media import MediaService

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/me")
def get_user_me(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get authenticated user profile."""
    return get_current_user_profile(current_user)


@users_router.post(
    "/me/avatar",
    response_model=StandardMediaResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload user profile avatar",
    description="Uploads and sets avatar for the authenticated user using safe replacement and Cloudinary optimization.",
)
def upload_avatar(
    file: UploadFile = File(..., description="Avatar image (JPEG, PNG, WebP)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Upload or replace avatar for authenticated user."""
    return MediaService(db).update_user_avatar(current_user, file)


@users_router.delete(
    "/me/avatar",
    response_model=StandardMediaResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete user profile avatar",
    description="Removes the authenticated user's avatar from Cloudinary and clears database reference.",
)
def delete_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Delete avatar for authenticated user."""
    return MediaService(db).delete_user_avatar(current_user)

