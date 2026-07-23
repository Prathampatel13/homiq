from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.auth import RefreshToken, Role, User
from app.security.passwords import hash_password, verify_password
from app.security.tokens import create_access_token, create_refresh_token


class UserCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.scalar(
            select(User).where(User.email == email)
        )

    def create_user(
        self,
        email: str,
        full_name: str,
        phone: str | None = None,
        role_name: str = "customer",
        password: str | None = None,
        password_hash: str | None = None,
    ) -> User:

        if password_hash is None:
            if password is None:
                raise ValueError("Password or password_hash is required")
            password_hash = hash_password(password)

        role = self.db.scalar(
            select(Role).where(Role.name == role_name)
        )

        if role is None:
            role = Role(name=role_name)
            self.db.add(role)
            self.db.flush()

        user = User(
            email=email,
            full_name=full_name,
            phone=phone,
            password_hash=password_hash,
            role=role,
            is_active=True,
            is_verified=False,
            is_superuser=False,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def authenticate(self, *, email: str, password: str) -> Optional[User]:
        print("=" * 50)
        print("LOGIN EMAIL:", email)

        user = self.get_user_by_email(email)

        print("USER FOUND:", user is not None)

        if not user:
            print("User not found")
            return None

        print("DB EMAIL:", user.email)
        print("HASH:", user.password_hash)

        result = verify_password(password, user.password_hash)

        print("PASSWORD MATCH:", result)

        if not result:
            print("Password verification failed")
            return None

        print("LOGIN SUCCESS")

        return user

    def update_password(
        self,
        user_id: int,
        new_password: str,
    ) -> Optional[User]:

        user = self.get_by_id(user_id)

        if user is None:
            return None

        user.password_hash = hash_password(new_password)

        self.db.commit()
        self.db.refresh(user)

        return user

    def update_last_login(self, user_id: int) -> None:
        user = self.get_by_id(user_id)

        if user is None:
            return

        user.updated_at = datetime.now(timezone.utc)

        self.db.commit()

    def get_refresh_token(
        self,
        refresh_token: str,
    ) -> Optional[RefreshToken]:

        return self.db.scalar(
            select(RefreshToken).where(
                RefreshToken.token == refresh_token,
                RefreshToken.revoked.is_(False),
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
        )

    def create_refresh_token(
        self,
        user_id: int,
        refresh_token: str,
    ) -> RefreshToken:

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        token_record = RefreshToken(
            user_id=user_id,
            token=refresh_token,
            expires_at=expires_at,
            revoked=False,
        )

        self.db.add(token_record)
        self.db.commit()
        self.db.refresh(token_record)

        return token_record

    def create_tokens(self, user: User) -> dict[str, str]:
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        self.create_refresh_token(user.id, refresh_token)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }