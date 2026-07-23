import os
import shutil
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import BASE_DIR, settings
from app.crud.customer import CustomerCRUD
from app.models.auth import User
from app.schemas.customer import (
    CustomerAddressCreate,
    CustomerAddressResponse,
    CustomerAddressUpdate,
    CustomerProfileResponse,
    CustomerProfileUpdate,
    ProfileImageResponse,
)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


class CustomerService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = CustomerCRUD(db)

    def _get_customer_or_404(self, user_id: int) -> Any:
        """Get customer profile for a user; create if not exists."""
        customer = self.crud.get_by_user_id(user_id)
        if not customer:
            customer = self.crud.create(user_id)
        return customer

    # ── Profile ───────────────────────────────────────────────────────

    def get_profile(self, current_user: User) -> CustomerProfileResponse:
        customer = self._get_customer_or_404(current_user.id)
        addresses = self.crud.get_addresses(customer.id)
        return self._build_profile_response(current_user, customer, addresses)

    def update_profile(
        self, current_user: User, payload: CustomerProfileUpdate
    ) -> CustomerProfileResponse:
        customer = self._get_customer_or_404(current_user.id)

        update_data = payload.model_dump(exclude_unset=True, exclude_none=True)

        # Separate user-level fields
        full_name = update_data.pop("full_name", None)

        # Update customer fields
        if update_data:
            self.crud.update(customer.id, update_data)

        # Update user-level fields
        if full_name:
            self.crud.update_user_name(current_user.id, full_name)

        # Refresh and return
        self.db.refresh(customer)
        addresses = self.crud.get_addresses(customer.id)
        return self._build_profile_response(current_user, customer, addresses)

    async def upload_profile_image(
        self, current_user: User, file: UploadFile
    ) -> ProfileImageResponse:
        customer = self._get_customer_or_404(current_user.id)

        # Validate file type
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}",
            )

        # Validate file size
        contents = await file.read()
        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image too large. Maximum size is 5 MB.",
            )
        await file.seek(0)

        # Ensure upload directory exists
        upload_dir = Path(BASE_DIR) / settings.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename
        ext = file.filename.split(".")[-1] if file.filename else "jpg"
        filename = f"customer_{current_user.id}_{uuid4().hex}.{ext}"
        file_path = upload_dir / filename

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Build URL path — relative URL for serving via static mount
        relative_path = f"{settings.UPLOAD_DIR}/{filename}".replace("\\", "/")
        self.crud.update(customer.id, {"profile_image": relative_path})

        return ProfileImageResponse(profile_image=relative_path)

    # ── Addresses ─────────────────────────────────────────────────────

    def get_addresses(
        self, current_user: User
    ) -> list[CustomerAddressResponse]:
        self._get_customer_or_404(current_user.id)
        addresses = self.crud.get_addresses(current_user.id)
        return [
            CustomerAddressResponse.model_validate(a) for a in addresses
        ]

    def get_address(
        self, current_user: User, address_id: int
    ) -> CustomerAddressResponse:
        self._get_customer_or_404(current_user.id)
        address = self.crud.get_address(current_user.id, address_id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )
        return CustomerAddressResponse.model_validate(address)

    def create_address(
        self, current_user: User, payload: CustomerAddressCreate
    ) -> CustomerAddressResponse:
        self._get_customer_or_404(current_user.id)
        data = payload.model_dump()
        address = self.crud.create_address(current_user.id, data)
        return CustomerAddressResponse.model_validate(address)

    def update_address(
        self,
        current_user: User,
        address_id: int,
        payload: CustomerAddressUpdate,
    ) -> CustomerAddressResponse:
        self._get_customer_or_404(current_user.id)
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )
        address = self.crud.update_address(current_user.id, address_id, data)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )
        return CustomerAddressResponse.model_validate(address)

    def delete_address(
        self, current_user: User, address_id: int
    ) -> dict[str, str]:
        self._get_customer_or_404(current_user.id)
        deleted = self.crud.delete_address(current_user.id, address_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )
        return {"message": "Address deleted successfully"}

    def set_default_address(
        self, current_user: User, address_id: int
    ) -> CustomerAddressResponse:
        self._get_customer_or_404(current_user.id)
        address = self.crud.set_default_address(current_user.id, address_id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )
        return CustomerAddressResponse.model_validate(address)

    # ── Helpers ───────────────────────────────────────────────────────

    def _build_profile_response(
        self,
        user: User,
        customer: Any,
        addresses: list[Any],
    ) -> CustomerProfileResponse:
        return CustomerProfileResponse(
            id=customer.id,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=customer.phone or user.phone,
            profile_image=customer.profile_image,
            address=customer.address,
            city=customer.city,
            state=customer.state,
            postal_code=customer.postal_code,
            latitude=customer.latitude,
            longitude=customer.longitude,
            preferred_language=customer.preferred_language,
            is_verified=user.is_verified,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
            addresses=[
                CustomerAddressResponse.model_validate(a) for a in addresses
            ],
        )

