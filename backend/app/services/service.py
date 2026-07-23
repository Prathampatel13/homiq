import os
import shutil
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import BASE_DIR, settings
from app.crud.services import ServicesCRUD
from app.models.auth import User
from app.models.services import Category
from app.schemas.services import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    ServiceCreate,
    ServiceImageResponse,
    ServiceListResponse,
    ServiceResponse,
    ServiceUpdate,
)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


class ServiceService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = ServicesCRUD(db)

    def _require_admin(self, current_user: User) -> None:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin credentials are required for this action.",
            )

    # ── Categories ─────────────────────────────────────────────────────

    def create_category(self, current_user: User, payload: CategoryCreate) -> CategoryResponse:
        self._require_admin(current_user)
        category = self.crud.create_category(payload.model_dump())
        return self._build_category_response(category)

    def get_category(self, category_id: int) -> CategoryResponse:
        category = self.crud.get_category(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )
        return self._build_category_response(category)

    def list_categories(self) -> list[CategoryResponse]:
        categories = self.crud.list_categories()
        return [self._build_category_response(category) for category in categories]

    def update_category(
        self, current_user: User, category_id: int, payload: CategoryUpdate
    ) -> CategoryResponse:
        self._require_admin(current_user)
        category = self.crud.update_category(category_id, payload.model_dump(exclude_unset=True, exclude_none=True))
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )
        return self._build_category_response(category)

    def delete_category(self, current_user: User, category_id: int) -> dict[str, str]:
        self._require_admin(current_user)
        deleted = self.crud.delete_category(category_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )
        return {"message": "Category deleted successfully."}

    # ── Services ───────────────────────────────────────────────────────

    def create_service(self, current_user: User, payload: ServiceCreate) -> ServiceResponse:
        self._require_admin(current_user)
        service = self.crud.create_service(payload.model_dump(exclude_none=True))
        return self._build_service_response(service)

    def get_service(self, service_id: int) -> ServiceResponse:
        service = self.crud.get_service(service_id)
        if not service or not service.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )
        return self._build_service_response(service)

    def list_services(
        self,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        category_name: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> ServiceListResponse:
        services, total = self.crud.list_services(
            search=search,
            category_id=category_id,
            category_name=category_name,
            min_price=min_price,
            max_price=max_price,
            min_duration=min_duration,
            max_duration=max_duration,
            page=page,
            per_page=per_page,
        )
        return ServiceListResponse(
            total=total,
            page=page,
            per_page=per_page,
            items=[self._build_service_response(service) for service in services],
        )

    def update_service(
        self, current_user: User, service_id: int, payload: ServiceUpdate
    ) -> ServiceResponse:
        self._require_admin(current_user)
        service = self.crud.update_service(
            service_id, payload.model_dump(exclude_unset=True, exclude_none=True)
        )
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )
        return self._build_service_response(service)

    def delete_service(self, current_user: User, service_id: int) -> dict[str, str]:
        self._require_admin(current_user)
        deleted = self.crud.delete_service(service_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )
        return {"message": "Service deleted successfully."}

    def upload_service_image(
        self, current_user: User, service_id: int, file: UploadFile
    ) -> ServiceImageResponse:
        self._require_admin(current_user)
        service = self.crud.get_service(service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found.",
            )

        image_url = self._store_image(file, service_id)
        self.crud.update_service(service_id, {"image_url": image_url})
        return ServiceImageResponse(image_url=image_url)

    async def _store_image(self, file: UploadFile, service_id: int) -> str:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}",
            )

        contents = await file.read()
        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image too large. Maximum size is 5 MB.",
            )
        await file.seek(0)

        upload_dir = Path(BASE_DIR) / settings.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)
        ext = file.filename.split('.')[-1] if file.filename else 'jpg'
        filename = f"service_image_{service_id}_{uuid4().hex}.{ext}"
        file_path = upload_dir / filename
        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)

        return f"{settings.UPLOAD_DIR}/{filename}".replace('\\', '/')

    def _build_category_response(self, category: Category) -> CategoryResponse:
        return CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            created_at=category.created_at,
        )

    def _build_service_response(self, service: Any) -> ServiceResponse:
        category_response = (
            self._build_category_response(service.category)
            if service.category is not None
            else None
        )
        return ServiceResponse(
            id=service.id,
            name=service.name,
            description=service.description,
            base_price=service.base_price,
            duration_minutes=service.duration_minutes,
            category_id=service.category_id,
            is_active=service.is_active,
            image_url=service.image_url,
            category=category_response,
            created_at=service.created_at,
            updated_at=service.updated_at,
        )
