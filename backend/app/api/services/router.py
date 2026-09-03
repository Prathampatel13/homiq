from typing import Any
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user
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
from app.services.service import ServiceService

router = APIRouter(prefix="/services", tags=["Services"])


# ==========================
# CATEGORY ROUTES
# ==========================

@router.get(
    "/categories",
    response_model=list[CategoryResponse],
)
def list_categories(db: Session = Depends(get_db)):
    return ServiceService(db).list_categories()


@router.get(
    "/categories/{category_id}",
    response_model=CategoryResponse,
)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return ServiceService(db).get_category(category_id)


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ServiceService(db).create_category(current_user, payload)


@router.put(
    "/categories/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ServiceService(db).update_category(
        current_user,
        category_id,
        payload,
    )


@router.delete(
    "/categories/{category_id}",
)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ServiceService(db).delete_category(
        current_user,
        category_id,
    )


# ==========================
# SERVICE ROUTES
# ==========================

@router.get(
    "/",
    response_model=ServiceListResponse,
)
def list_services(
    search: str | None = None,
    category_id: int | None = None,
    category_name: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_duration: int | None = None,
    max_duration: int | None = None,
    page: int = 1,
    per_page: int = 20,
    limit: int | None = None,
    db: Session = Depends(get_db),
):
    effective_per_page = limit if limit is not None else per_page
    return ServiceService(db).list_services(
        search=search,
        category_id=category_id,
        category_name=category_name,
        min_price=min_price,
        max_price=max_price,
        min_duration=min_duration,
        max_duration=max_duration,
        page=page,
        per_page=effective_per_page,
    )


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
):
    return ServiceService(db).get_service(service_id)


@router.post(
    "/",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service(
    payload: ServiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ServiceService(db).create_service(
        current_user,
        payload,
    )


@router.put(
    "/{service_id}",
    response_model=ServiceResponse,
)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ServiceService(db).update_service(
        current_user,
        service_id,
        payload,
    )


@router.delete(
    "/{service_id}",
)
def delete_service(
    service_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ServiceService(db).delete_service(
        current_user,
        service_id,
    )


@router.post(
    "/{service_id}/image",
    response_model=ServiceImageResponse,
)
async def upload_service_image(
    service_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await ServiceService(db).upload_service_image(
        current_user,
        service_id,
        file,
    )


# ── Service Gallery Endpoints ────────────────────────────────────────────

from app.schemas.media import MediaAssetResponse, StandardMediaResponse
from app.services.media import MediaService


@router.post(
    "/{service_id}/gallery",
    response_model=StandardMediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload service gallery image",
    description="Uploads a photo to a service's public gallery (Admin or Company only).",
)
def upload_service_gallery_image(
    service_id: int,
    file: UploadFile = File(..., description="Gallery image (JPEG, PNG, WebP)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Upload service gallery image."""
    return MediaService(db).upload_service_gallery(current_user, service_id, file)


@router.get(
    "/{service_id}/gallery",
    response_model=list[MediaAssetResponse],
    summary="List service gallery images",
    description="Returns all gallery photos for a given service.",
)
def list_service_gallery_images(
    service_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """List service gallery photos."""
    return MediaService(db).list_service_gallery(service_id)


@router.delete(
    "/{service_id}/gallery/{asset_id}",
    response_model=StandardMediaResponse,
    summary="Delete service gallery image",
    description="Deletes an image from a service gallery (Admin only).",
)
def delete_service_gallery_image(
    service_id: int,
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Delete service gallery photo."""
    return MediaService(db).delete_service_gallery(current_user, service_id, asset_id)