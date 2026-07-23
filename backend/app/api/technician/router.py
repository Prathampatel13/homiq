from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user
from app.schemas.technician import (
    GovernmentIdImageResponse,
    ProfileImageResponse,
    TechnicianCreate,
    TechnicianResponse,
    TechnicianUpdate,
)
from app.services.technician import TechnicianService

router = APIRouter(prefix="/technician", tags=["Technician"])


@router.get(
    "/profile",
    response_model=TechnicianResponse,
    summary="Get technician profile",
    description="Returns the authenticated technician's profile and metadata.",
)
def get_profile(
    current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    service = TechnicianService(db)
    return service.get_profile(current_user)


@router.put(
    "/profile",
    response_model=TechnicianResponse,
    summary="Update technician profile",
    description="Update technician profile fields such as specialization, experience, skills, availability, and service radius.",
)
def update_profile(
    payload: TechnicianUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TechnicianService(db)
    return service.update_profile(current_user, payload)


@router.post(
    "/profile/image",
    response_model=ProfileImageResponse,
    summary="Upload profile image",
    description="Upload a technician profile image for the authenticated user.",
)
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TechnicianService(db)
    return await service.upload_profile_image(current_user, file)


@router.post(
    "/profile/government-id",
    response_model=GovernmentIdImageResponse,
    summary="Upload government ID image",
    description="Upload a technician's government-issued ID image for verification.",
)
async def upload_government_id(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = TechnicianService(db)
    return await service.upload_government_id(current_user, file)


@router.get(
    "/",
    response_model=list[TechnicianResponse],
    summary="List technicians",
    description="List technicians with optional filters for specialization, availability, and online status.",
)
def list_technicians(
    specialization: str | None = None,
    availability: bool | None = None,
    is_online: bool | None = None,
    db: Session = Depends(get_db),
):
    service = TechnicianService(db)
    return service.list_technicians(
        specialization=specialization,
        availability=availability,
        online=is_online,
    )
