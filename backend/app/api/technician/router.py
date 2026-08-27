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
    TechnicianActionRequest,
    TechnicianAvailabilityResponse,
    TechnicianAvailabilityUpdate,
    TechnicianCreate,
    TechnicianEarningsResponse,
    TechnicianJobListResponse,
    TechnicianJobResponse,
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


@router.patch(
    "/online",
    response_model=TechnicianAvailabilityResponse,
    summary="Set technician online",
    description="Marks the technician as online and available for bookings.",
)
def set_online(
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    service = TechnicianService(db)
    return service.set_online(current_user)


@router.patch(
    "/offline",
    response_model=TechnicianAvailabilityResponse,
    summary="Set technician offline",
    description="Marks the technician as offline and unavailable.",
)
def set_offline(
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    service = TechnicianService(db)
    return service.set_offline(current_user)


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


# ── Jobs & Bookings ───────────────────────────────────────────────────


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


@router.get(
    "/bookings",
    response_model=TechnicianJobListResponse,
    summary="Get technician bookings",
    description="Returns bookings assigned to the authenticated technician, optionally filtered by status.",
)
def get_technician_bookings(
    status: str | None = None,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Get bookings assigned to the authenticated technician."""
    service = TechnicianService(db)
    return service.get_my_jobs(
        current_user, status=status, offset=offset, limit=limit
    )


@router.get(
    "/bookings/active",
    response_model=TechnicianJobListResponse,
    summary="Get active technician bookings",
    description="Returns active (in-flight) bookings assigned to the technician.",
)
def get_active_bookings(
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Get active in-flight bookings assigned to technician."""
    service = TechnicianService(db)
    return service.get_active_bookings(current_user, offset=offset, limit=limit)


@router.get(
    "/history",
    response_model=TechnicianJobListResponse,
    summary="Get technician booking history",
    description="Returns past/completed booking history for the technician.",
)
def get_booking_history(
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Get completed/past booking history for technician."""
    service = TechnicianService(db)
    return service.get_booking_history(current_user, offset=offset, limit=limit)


@router.get(
    "/customers/{customer_id}/history",
    response_model=TechnicianJobListResponse,
    summary="Get customer booking history",
    description="Returns past booking history of a specific customer.",
)
def get_customer_history_for_tech(
    customer_id: int,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Get past/completed booking history of a customer."""
    service = TechnicianService(db)
    return service.get_customer_history(current_user, customer_id, offset=offset, limit=limit)


# ── Booking Action Workflow ───────────────────────────────────────────


@router.patch(
    "/bookings/{id}/accept",
    response_model=TechnicianJobResponse,
    summary="Accept booking",
    description="Accept an assigned booking.",
)
def accept_booking(
    id: int,
    payload: TechnicianActionRequest = TechnicianActionRequest(),
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Accept an assigned booking."""
    service = TechnicianService(db)
    return service.accept_booking(current_user, id, reason=payload.reason)


@router.patch(
    "/bookings/{id}/reject",
    response_model=TechnicianJobResponse,
    summary="Reject booking",
    description="Reject an assigned booking.",
)
def reject_booking(
    id: int,
    payload: TechnicianActionRequest = TechnicianActionRequest(),
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Reject an assigned booking."""
    service = TechnicianService(db)
    return service.reject_booking(current_user, id, reason=payload.reason)


@router.patch(
    "/bookings/{id}/start-trip",
    response_model=TechnicianJobResponse,
    summary="Start trip",
    description="Start navigation to job location (marks status as on_the_way).",
)
def start_trip(
    id: int,
    payload: TechnicianActionRequest = TechnicianActionRequest(),
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Start trip to customer location."""
    service = TechnicianService(db)
    return service.start_trip(current_user, id, reason=payload.reason)


@router.patch(
    "/bookings/{id}/arrived",
    response_model=TechnicianJobResponse,
    summary="Mark arrived",
    description="Mark arrival at customer location (marks status as arrived).",
)
def mark_arrived(
    id: int,
    payload: TechnicianActionRequest = TechnicianActionRequest(),
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Mark arrival at job location."""
    service = TechnicianService(db)
    return service.mark_arrived(current_user, id, reason=payload.reason)


@router.patch(
    "/bookings/{id}/start-service",
    response_model=TechnicianJobResponse,
    summary="Start service",
    description="Start working on the service (marks status as in_progress).",
)
def start_service(
    id: int,
    payload: TechnicianActionRequest = TechnicianActionRequest(),
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Start performing service."""
    service = TechnicianService(db)
    return service.start_service(current_user, id, reason=payload.reason)


@router.patch(
    "/bookings/{id}/complete",
    response_model=TechnicianJobResponse,
    summary="Complete service",
    description="Complete the service (marks status as completed).",
)
def complete_service(
    id: int,
    payload: TechnicianActionRequest = TechnicianActionRequest(),
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Complete service work."""
    service = TechnicianService(db)
    return service.complete_service(current_user, id, reason=payload.reason)


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


# ── Technician Media: Avatar, Portfolio, Certificates ────────────────────

from app.schemas.media import MediaAssetResponse, StandardMediaResponse
from app.services.media import MediaService


@router.post(
    "/me/avatar",
    response_model=StandardMediaResponse,
    summary="Upload technician avatar",
    description="Uploads and updates avatar for the authenticated technician with atomic rollback safety.",
)
def upload_tech_avatar(
    file: UploadFile = File(..., description="Avatar image"),
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Upload technician avatar."""
    return MediaService(db).update_user_avatar(current_user, file)


@router.delete(
    "/me/avatar",
    response_model=StandardMediaResponse,
    summary="Delete technician avatar",
    description="Removes avatar for the authenticated technician.",
)
def delete_tech_avatar(
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Delete technician avatar."""
    return MediaService(db).delete_user_avatar(current_user)


@router.post(
    "/me/portfolio",
    response_model=StandardMediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload portfolio work sample",
    description="Uploads a work sample to the technician's public portfolio.",
)
def upload_portfolio_work(
    file: UploadFile = File(..., description="Portfolio image (JPEG, PNG, WebP)"),
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Upload portfolio work sample."""
    return MediaService(db).upload_technician_portfolio(current_user, file)


@router.get(
    "/me/portfolio",
    response_model=list[MediaAssetResponse],
    summary="List technician portfolio work",
    description="Returns all portfolio work samples uploaded by the authenticated technician.",
)
def list_my_portfolio(
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """List portfolio items."""
    return MediaService(db).list_technician_portfolio(current_user)


@router.delete(
    "/me/portfolio/{asset_id}",
    response_model=StandardMediaResponse,
    summary="Delete portfolio work sample",
    description="Deletes a portfolio work sample owned by the technician.",
)
def delete_my_portfolio(
    asset_id: int,
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Delete portfolio item."""
    return MediaService(db).delete_technician_portfolio(current_user, asset_id)


@router.post(
    "/me/certificates",
    response_model=StandardMediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload professional certificate",
    description="Uploads a certificate document or image (PDF, JPEG, PNG, WebP) for the authenticated technician.",
)
def upload_certificate_doc(
    file: UploadFile = File(..., description="Certificate file (Image or PDF)"),
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Upload professional certificate."""
    return MediaService(db).upload_technician_certificate(current_user, file)


@router.get(
    "/me/certificates",
    response_model=list[MediaAssetResponse],
    summary="List technician certificates",
    description="Returns all certificates uploaded by the authenticated technician.",
)
def list_my_certificates(
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """List certificates."""
    return MediaService(db).list_technician_certificates(current_user)


@router.delete(
    "/me/certificates/{asset_id}",
    response_model=StandardMediaResponse,
    summary="Delete professional certificate",
    description="Deletes a certificate owned by the technician.",
)
def delete_my_certificate(
    asset_id: int,
    current_user: User = Depends(get_current_technician),
    db: Session = Depends(get_db),
) -> Any:
    """Delete certificate."""
    return MediaService(db).delete_technician_certificate(current_user, asset_id)


technicians_router = APIRouter(prefix="/technicians", tags=["Technicians"])

technicians_router.add_api_route("/me/avatar", upload_tech_avatar, methods=["POST"], response_model=StandardMediaResponse)
technicians_router.add_api_route("/me/avatar", delete_tech_avatar, methods=["DELETE"], response_model=StandardMediaResponse)
technicians_router.add_api_route("/me/portfolio", upload_portfolio_work, methods=["POST"], response_model=StandardMediaResponse, status_code=status.HTTP_201_CREATED)
technicians_router.add_api_route("/me/portfolio", list_my_portfolio, methods=["GET"], response_model=list[MediaAssetResponse])
technicians_router.add_api_route("/me/portfolio/{asset_id}", delete_my_portfolio, methods=["DELETE"], response_model=StandardMediaResponse)
technicians_router.add_api_route("/me/certificates", upload_certificate_doc, methods=["POST"], response_model=StandardMediaResponse, status_code=status.HTTP_201_CREATED)
technicians_router.add_api_route("/me/certificates", list_my_certificates, methods=["GET"], response_model=list[MediaAssetResponse])
technicians_router.add_api_route("/me/certificates/{asset_id}", delete_my_certificate, methods=["DELETE"], response_model=StandardMediaResponse)




