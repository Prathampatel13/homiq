import os
import shutil
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import BASE_DIR, settings
from app.crud.technician import TechnicianCRUD
from app.models.auth import User
from app.schemas.technician import (
    GovernmentIdImageResponse,
    ProfileImageResponse,
    TechnicianCreate,
    TechnicianResponse,
    TechnicianUpdate,
)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


class TechnicianService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = TechnicianCRUD(db)

    def _get_technician_or_404(self, user_id: int):
        technician = self.crud.get_by_user_id(user_id)
        if not technician:
            technician = self.crud.create(user_id)
        return technician

    def get_profile(self, current_user: User) -> TechnicianResponse:
        technician = self._get_technician_or_404(current_user.id)
        return self._build_response(current_user, technician)

    def update_profile(
        self, current_user: User, payload: TechnicianUpdate
    ) -> TechnicianResponse:
        technician = self._get_technician_or_404(current_user.id)
        update_data = payload.model_dump(exclude_unset=True, exclude_none=True)
        full_name = update_data.pop("full_name", None)

        if update_data:
            self.crud.update(technician.id, update_data)
            self.db.refresh(technician)

        if full_name:
            self.crud.update_user_name(current_user.id, full_name)
            self.db.refresh(technician)

        return self._build_response(current_user, technician)

    async def upload_profile_image(
        self, current_user: User, file: UploadFile
    ) -> ProfileImageResponse:
        technician = self._get_technician_or_404(current_user.id)
        relative_path = await self._store_image(file, current_user.id, "technician_profile")
        self.crud.update(technician.id, {"profile_image": relative_path})
        return ProfileImageResponse(profile_image=relative_path)

    async def upload_government_id(
        self, current_user: User, file: UploadFile
    ) -> GovernmentIdImageResponse:
        technician = self._get_technician_or_404(current_user.id)
        relative_path = await self._store_image(file, current_user.id, "technician_gov_id")
        self.crud.update(technician.id, {"government_id_image": relative_path})
        return GovernmentIdImageResponse(government_id_image=relative_path)

    def list_technicians(
        self,
        specialization: str | None = None,
        availability: bool | None = None,
        online: bool | None = None,
    ) -> list[TechnicianResponse]:
        technicians = self.crud.list_technicians(
            specialization=specialization,
            availability=availability,
            online=online,
        )
        return [self._build_response(t.user, t) for t in technicians]

    async def _store_image(self, file: UploadFile, user_id: int, prefix: str) -> str:
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
        ext = file.filename.split(".")[-1] if file.filename else "jpg"
        filename = f"{prefix}_{user_id}_{uuid4().hex}.{ext}"
        file_path = upload_dir / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return f"{settings.UPLOAD_DIR}/{filename}".replace("\\", "/")

    def _build_response(self, user: User, technician: Any) -> TechnicianResponse:
        return TechnicianResponse(
            id=technician.id,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            specialization=technician.specialization,
            experience_years=technician.experience_years,
            skills=technician.skills or [],
            languages=technician.languages or [],
            working_hours=technician.working_hours,
            availability=technician.availability,
            latitude=technician.latitude,
            longitude=technician.longitude,
            service_radius_km=technician.service_radius_km,
            is_online=technician.is_online,
            rating=technician.rating,
            reviews_count=technician.reviews_count,
            profile_image=technician.profile_image,
            government_id_image=technician.government_id_image,
            created_at=technician.created_at,
            updated_at=technician.updated_at,
        )
