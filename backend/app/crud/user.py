from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, or_, select
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

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.get_by_id(user_id)

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

        # Normalize role name
        normalized_role = role_name.strip().lower()

        role_mapping = {
            "customer": "customer",
            "role_customer": "customer",
            "technician": "technician",
            "role_technician": "technician",
            "company": "company",
            "role_company": "company",
            "admin": "admin",
            "role_admin": "admin",
        }

        normalized_role = role_mapping.get(normalized_role, normalized_role)

        role = self.db.scalar(
            select(Role).where(Role.name == normalized_role)
        )

        if role is None:
            raise ValueError(f"Invalid role: {role_name}")

        user = User(
            email=email,
            full_name=full_name,
            phone=phone,
            password_hash=password_hash,
            role=role,
            is_active=True,
            is_verified=False,
            is_superuser=(normalized_role == "admin"),
        )

        self.db.add(user)
        self.db.flush()

        from app.models.users import Company, Customer, Technician

        if normalized_role == "customer":
            self.db.add(
                Customer(
                    user_id=user.id,
                    phone=phone,
                )
            )

        elif normalized_role == "technician":
            self.db.add(
                Technician(
                    user_id=user.id,
                )
            )

        elif normalized_role == "company":
            self.db.add(
                Company(
                    user_id=user.id,
                    company_name=full_name,
                )
            )

        self.db.commit()
        self.db.refresh(user)

        return user

    def get_user_by_identifier(self, identifier: str) -> Optional[User]:
        return self.db.scalar(
            select(User).where(
                or_(
                    User.email == identifier,
                    User.phone == identifier,
                    User.full_name == identifier
                )
            )
        )

    def authenticate(self, *, identifier: str, password: str) -> Optional[User]:
        print("=" * 50)
        print("LOGIN IDENTIFIER:", identifier)

        user = self.get_user_by_identifier(identifier)

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

    def update_avatar_url(
        self,
        user_id: int,
        avatar_url: Optional[str],
    ) -> Optional[User]:
        user = self.get_by_id(user_id)
        if user is None:
            return None
        user.avatar_url = avatar_url
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

    # ── Admin User Management CRUD ─────────────────────────────────────

    def list_users(
        self,
        query: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """List users with search, role filter, and active status filter."""
        stmt = select(User).join(Role, User.role_id == Role.id)
        if query:
            stmt = stmt.where(
                or_(
                    User.full_name.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                    User.phone.ilike(f"%{query}%"),
                )
            )
        if role:
            stmt = stmt.where(Role.name.ilike(role))
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)

        stmt = stmt.order_by(User.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_users(
        self,
        query: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """Count users matching search and filter criteria."""
        stmt = select(func.count(User.id)).join(Role, User.role_id == Role.id)
        if query:
            stmt = stmt.where(
                or_(
                    User.full_name.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                    User.phone.ilike(f"%{query}%"),
                )
            )
        if role:
            stmt = stmt.where(Role.name.ilike(role))
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)

        return self.db.scalar(stmt) or 0

    def set_active_status(self, user_id: int, is_active: bool) -> Optional[User]:
        """Activate or suspend a user account."""
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.is_active = is_active
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_verified_status(self, user_id: int, is_verified: bool) -> Optional[User]:
        """Approve or reject verification for a user."""
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.is_verified = is_verified
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user account."""
        user = self.get_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True

