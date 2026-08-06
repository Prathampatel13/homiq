from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.tokens import decode_token

security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:

    token = credentials.credentials

    try:
        payload: dict[str, Any] = decode_token(token)

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive account",
        )

    return user


# ==========================================================
# CUSTOMER
# ==========================================================

def get_current_customer(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role is None:
        raise HTTPException(
            status_code=403,
            detail="Role not assigned."
        )

    if current_user.role.name.lower() != "customer":
        raise HTTPException(
            status_code=403,
            detail="Customer access required."
        )

    return current_user


# ==========================================================
# TECHNICIAN
# ==========================================================

def get_current_technician(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role is None:
        raise HTTPException(
            status_code=403,
            detail="Role not assigned."
        )

    if current_user.role.name.lower() != "technician":
        raise HTTPException(
            status_code=403,
            detail="Technician access required."
        )

    return current_user


# ==========================================================
# COMPANY
# ==========================================================

def get_current_company(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role is None:
        raise HTTPException(
            status_code=403,
            detail="Role not assigned."
        )

    if current_user.role.name.lower() != "company":
        raise HTTPException(
            status_code=403,
            detail="Company access required."
        )

    return current_user


# ==========================================================
# ADMIN
# ==========================================================

def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:

    print("=" * 50)
    print("USER ID:", current_user.id)
    print("EMAIL:", current_user.email)
    print("ROLE ID:", current_user.role_id)
    print("SUPERUSER:", current_user.is_superuser)
    print("=" * 50)

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Admin access required."
        )

    return current_user


# ==========================================================
# OPTIONAL USER
# ==========================================================

optional_security_scheme = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(optional_security_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if not credentials:
        return None
    try:
        return get_current_user(credentials=credentials, db=db)
    except HTTPException:
        return None