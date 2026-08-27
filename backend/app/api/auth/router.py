from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user import UserCRUD
from app.database.session import get_db
from app.models.auth import User
from app.schemas.auth import ForgotPasswordRequest, LoginRequest, RegisterRequest, ResetPasswordRequest, Token
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

    user = crud.create_user(
        email=str(payload.email),
        password=payload.password,
        full_name=payload.full_name,
        phone=payload.phone,
        role_name=payload.role,
    )
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
def refresh_token(refresh_token: str, db: Session = Depends(get_db)) -> Token:
    crud = UserCRUD(db)
    record = crud.get_refresh_token(refresh_token)
    if not record:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = crud.get_user_by_id(record.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    tokens = crud.create_tokens(user)
    return Token(**tokens)


from jose import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.services.email import send_email_in_background

@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    crud = UserCRUD(db)
    user = crud.get_user_by_email(payload.email)
    if user:
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
        reset_token = jwt.encode(
            {"sub": str(user.id), "type": "reset", "exp": expire},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
        
        html_body = f"""
        <h3>Reset Your Password</h3>
        <p>Hi {user.full_name},</p>
        <p>You requested a password reset. Click the link below to set a new password:</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        <p>This link expires in 1 hour.</p>
        <p>If you didn't request this, you can safely ignore this email.</p>
        """
        send_email_in_background(
            subject="Password Reset - HomiQ",
            email_to=user.email,
            body=html_body
        )
        
    return {"message": "If an account with that email exists, password reset instructions have been sent."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    from jose import JWTError
    try:
        payload_data = jwt.decode(payload.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload_data.get("type") != "reset":
            raise HTTPException(status_code=400, detail="Invalid token type")
        user_id = int(payload_data.get("sub"))
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
    crud = UserCRUD(db)
    user = crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    
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

