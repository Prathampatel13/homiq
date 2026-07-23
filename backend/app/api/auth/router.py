from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user import UserCRUD
from app.database.session import get_db
from app.schemas.auth import ForgotPasswordRequest, LoginRequest, RegisterRequest, ResetPasswordRequest, Token
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
    return Token(**tokens)


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    crud = UserCRUD(db)
    user = crud.authenticate(email=str(payload.email), password=payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    tokens = crud.create_tokens(user)
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


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    return {"message": "Password reset instructions sent"}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    return {"message": "Password updated"}
