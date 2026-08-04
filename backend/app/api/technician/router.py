from typing import Any

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.schemas.dashboard import TechnicianDashboardResponse
from app.security.deps import get_current_technician, get_current_user
from app.schemas.technician import (
    GovernmentIdImageResponse,
    ProfileImageResponse,
    TechnicianAvailabilityResponse,
    TechnicianAvailabilityUpdate,
    TechnicianCreate,
    TechnicianEarningsResponse,
    TechnicianJobListResponse,
    TechnicianResponse,
    TechnicianUpdate,
)
from app.services.technician import TechnicianService
from app.services.technician_dashboard import TechnicianDashboardService

router = APIRouter(prefix="/technician", tags=["Technician"])


@router.get(
    "/profile",
    response_model=TechnicianResponse,
    summary="Get technician profile",
    description="Returns the authenticated technician's profile and metadata.",
)
def get_profile(
    current_user=Depends(get_current_technician), db: Session = Depends(get_db)
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
    current_user=Depends(get_current_technician),
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
    current_user=Depends(get_current_technician),
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
    current_user=Depends(get_current_technician),
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


# ── Jobs ──────────────────────────────────────────────────────────────


@router.get(
    "/jobs",
    response_model=TechnicianJobListResponse,
    summary="List my jobs",
    description="Returns the jobs (bookings) assigned to the authenticated technician, optionally filtered by status.",
)
def get_my_jobs(
    status: str | None = None,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """List jobs assigned to the authenticated technician."""
    service = TechnicianService(db)
    return service.get_my_jobs(
        current_user, status=status, offset=offset, limit=limit
    )


# ── Earnings ──────────────────────────────────────────────────────────


@router.get(
    "/earnings",
    response_model=TechnicianEarningsResponse,
    summary="My earnings",
    description="Returns the authenticated technician's earnings summary including total, pending, and completed/paid job counts.",
)
def get_my_earnings(
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Get the authenticated technician's earnings summary."""
    service = TechnicianService(db)
    return service.get_my_earnings(current_user)


# ── Availability ──────────────────────────────────────────────────────


@router.put(
    "/availability",
    response_model=TechnicianAvailabilityResponse,
    summary="Update availability",
    description="Update the technician's availability and/or online status.",
)
def update_availability(
    payload: TechnicianAvailabilityUpdate,
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Update the technician's availability and online status."""
    service = TechnicianService(db)
    return service.update_availability(current_user, payload)


# ── Dashboard ──────────────────────────────────────────────────────────


@router.get(
    "/dashboard",
    response_model=TechnicianDashboardResponse,
    summary="Technician dashboard",
    description="Returns the authenticated technician's dashboard with job statistics, earnings, ratings, today's jobs, and next pending job.",
)
def get_technician_dashboard(
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Get the technician dashboard with job stats and today's schedule."""
    service = TechnicianDashboardService(db)
    return service.get_dashboard(current_user)
