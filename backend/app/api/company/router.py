"""
Company profile management endpoints.

Provides:
- Company profile retrieval and update (JWT-protected, company role required)
- Public listing of companies (no authentication)
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_company
from app.schemas.company import CompanyProfileResponse, CompanyProfileUpdate
from app.services.company import CompanyService

router = APIRouter(prefix="/company", tags=["Company"])


@router.get(
    "/profile",
    response_model=CompanyProfileResponse,
    summary="Get company profile",
    description="Returns the authenticated company's profile information.",
)
def get_profile(
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Any:
    """Fetch the authenticated company's profile."""
    return CompanyService(db).get_profile(current_user)


@router.put(
    "/profile",
    response_model=CompanyProfileResponse,
    summary="Update company profile",
    description="Update company fields such as name, industry, description, and website. Only provided fields are updated.",
)
def update_profile(
    payload: CompanyProfileUpdate,
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Any:
    """Update the company's profile. Omitting a field leaves it unchanged."""
    return CompanyService(db).update_profile(current_user, payload)


@router.get(
    "/",
    response_model=list[CompanyProfileResponse],
    summary="List companies",
    description="Returns a paginated list of companies. Optionally filter by industry. Public endpoint.",
)
def list_companies(
    industry: str | None = None,
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> Any:
    """List all companies (public metadata)."""
    return CompanyService(db).list_companies(
        industry=industry,
        offset=offset,
        limit=limit,
    )


# ── Company Media Endpoints (Logo & Gallery) ─────────────────────────────

from fastapi import File, UploadFile, status
from app.schemas.media import MediaAssetResponse, StandardMediaResponse
from app.services.media import MediaService


@router.post(
    "/me/logo",
    response_model=StandardMediaResponse,
    summary="Upload company logo",
    description="Uploads and updates brand logo for the authenticated company.",
)
def upload_logo(
    file: UploadFile = File(..., description="Logo image (JPEG, PNG, WebP)"),
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Any:
    """Upload company logo."""
    return MediaService(db).upload_company_logo(current_user, file)


@router.post(
    "/me/gallery",
    response_model=StandardMediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload company gallery image",
    description="Uploads photo to company portfolio/gallery.",
)
def upload_gallery_image(
    file: UploadFile = File(..., description="Gallery image (JPEG, PNG, WebP)"),
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Any:
    """Upload company gallery image."""
    return MediaService(db).upload_company_gallery(current_user, file)


@router.get(
    "/me/gallery",
    response_model=list[MediaAssetResponse],
    summary="List my company gallery",
    description="Returns gallery images uploaded by the authenticated company.",
)
def list_my_gallery(
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Any:
    """List authenticated company gallery images."""
    return MediaService(db).list_company_gallery(current_user.id)


@router.get(
    "/{company_id}/gallery",
    response_model=list[MediaAssetResponse],
    summary="List company gallery by ID",
    description="Public listing of gallery photos for a given company.",
)
def list_company_gallery_public(
    company_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """Public listing of company gallery photos."""
    return MediaService(db).list_company_gallery(company_id)


@router.delete(
    "/me/gallery/{asset_id}",
    response_model=StandardMediaResponse,
    summary="Delete company gallery image",
    description="Deletes a gallery image owned by the authenticated company.",
)
def delete_gallery_image(
    asset_id: int,
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Any:
    """Delete company gallery image."""
    return MediaService(db).delete_company_gallery(current_user, asset_id)


companies_router = APIRouter(prefix="/companies", tags=["Companies"])

companies_router.add_api_route("/me/logo", upload_logo, methods=["POST"], response_model=StandardMediaResponse)
companies_router.add_api_route("/me/gallery", upload_gallery_image, methods=["POST"], response_model=StandardMediaResponse, status_code=status.HTTP_201_CREATED)
companies_router.add_api_route("/me/gallery", list_my_gallery, methods=["GET"], response_model=list[MediaAssetResponse])
companies_router.add_api_route("/{company_id}/gallery", list_company_gallery_public, methods=["GET"], response_model=list[MediaAssetResponse])
companies_router.add_api_route("/me/gallery/{asset_id}", delete_gallery_image, methods=["DELETE"], response_model=StandardMediaResponse)


