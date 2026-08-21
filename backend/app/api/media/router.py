"""
Cloudinary Media & Document Management endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.models.media import MediaAssetType
from app.schemas.media import (
    DocumentApprovalPayload,
    DocumentTypeEnum,
    MediaAssetListResponse,
    MediaAssetResponse,
    MediaOptimizedUrlRequest,
    MediaOptimizedUrlResponse,
    MediaResponse,
    StandardMediaResponse,
    TechnicianDocumentResponse,
)
from app.security.deps import get_current_user
from app.services.media import MediaService

router = APIRouter(tags=["Media & Documents"])


# ─── CENTRAL MEDIA ASSET ENDPOINTS ──────────────────────────────────────────


@router.post(
    "/media/upload",
    response_model=MediaAssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload media asset",
    description="Uploads an image or document to Cloudinary with deterministic folder routing, validation, and database tracking.",
)
def upload_media(
    file: UploadFile = File(...),
    asset_type: MediaAssetType = Form(MediaAssetType.PROFILE_AVATAR),
    owner_id: Optional[int] = Form(None),
    owner_type: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Upload media asset to Cloudinary and persist metadata."""
    return MediaService(db).upload_asset(
        current_user=current_user,
        file=file,
        asset_type=asset_type,
        owner_id=owner_id,
        owner_type=owner_type,
    )


@router.get(
    "/media/owner/{owner_type}/{owner_id}",
    response_model=MediaAssetListResponse,
    summary="List media assets by owner",
    description="Returns all media assets associated with an entity (user, technician, company, service, booking, etc.).",
)
def list_owner_media(
    owner_type: str,
    owner_id: int,
    asset_type: Optional[MediaAssetType] = Query(None),
    db: Session = Depends(get_db),
) -> Any:
    """List media assets for a given owner."""
    return MediaService(db).list_owner_assets(
        owner_id=owner_id,
        owner_type=owner_type,
        asset_type=asset_type,
    )


@router.get(
    "/media/{public_id:path}",
    response_model=MediaAssetResponse,
    summary="Get media asset details",
    description="Returns metadata and optimized Cloudinary URLs for a media asset by its public ID.",
)
def get_media(
    public_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """Get media asset details by public ID."""
    return MediaService(db).get_media_details(public_id)


@router.delete(
    "/media/{public_id:path}",
    status_code=status.HTTP_200_OK,
    summary="Delete media asset",
    description="Deletes a media asset from Cloudinary and removes its record from the database.",
)
def delete_media(
    public_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Delete media asset by public ID."""
    return MediaService(db).delete_media(current_user, public_id)


@router.patch(
    "/media/{public_id:path}",
    response_model=MediaAssetResponse,
    summary="Replace media asset",
    description="Replaces an existing Cloudinary asset with a newly uploaded file.",
)
def replace_media(
    public_id: str,
    file: UploadFile = File(...),
    asset_type: Optional[MediaAssetType] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Replace media asset."""
    return MediaService(db).replace_media(
        current_user=current_user,
        public_id=public_id,
        file=file,
        asset_type=asset_type,
    )


@router.post(
    "/media/transform/{public_id:path}",
    response_model=MediaOptimizedUrlResponse,
    summary="Generate optimized image URL",
    description="Generates an on-the-fly Cloudinary transformation URL with dynamic dimensions, cropping, format, and compression.",
)
def generate_transformed_url(
    public_id: str,
    payload: MediaOptimizedUrlRequest,
    db: Session = Depends(get_db),
) -> Any:
    """Generate transformed/optimized URL for an asset."""
    return MediaService(db).get_optimized_url(public_id, payload)


# ─── TECHNICIAN DOCUMENT VERIFICATION ────────────────────────────────────


@router.post(
    "/technician/documents",
    response_model=TechnicianDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload technician verification document",
    description="Technicians upload verification documents (Aadhaar, PAN, License, Certificate) for verification.",
)
def upload_technician_document(
    doc_type: DocumentTypeEnum = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Upload technician verification document."""
    return MediaService(db).upload_technician_document(current_user, doc_type=doc_type, file=file)


@router.get(
    "/technician/documents",
    response_model=list[TechnicianDocumentResponse],
    summary="Get technician verification documents",
    description="Returns uploaded verification documents for the authenticated technician.",
)
def get_technician_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get technician verification documents."""
    return MediaService(db).get_technician_documents(current_user)


# ─── ADMIN VERIFICATION WORKFLOW ──────────────────────────────────────────


@router.patch(
    "/admin/documents/{doc_id}/approve",
    response_model=TechnicianDocumentResponse,
    summary="Approve technician document",
    description="**Admin only.** Approves a technician verification document.",
)
def approve_technician_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Approve technician document."""
    return MediaService(db).approve_technician_document(current_user, doc_id)


@router.patch(
    "/admin/documents/{doc_id}/reject",
    response_model=TechnicianDocumentResponse,
    summary="Reject technician document",
    description="**Admin only.** Rejects a technician verification document with a reason.",
)
def reject_technician_document(
    doc_id: str,
    payload: DocumentApprovalPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Reject technician document."""
    return MediaService(db).reject_technician_document(current_user, doc_id, reason=payload.rejection_reason)


# ─── COMPLAINT EVIDENCE ENDPOINTS ────────────────────────────────────────


@router.post(
    "/complaints/{complaint_id}/attachments",
    response_model=StandardMediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload complaint evidence",
    description="Uploads photo/document evidence for a customer complaint.",
)
def upload_complaint_evidence(
    complaint_id: int,
    file: UploadFile = File(..., description="Evidence file (Image or PDF)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Upload complaint evidence attachment."""
    return MediaService(db).upload_complaint_attachment(current_user, complaint_id, file)


@router.get(
    "/complaints/{complaint_id}/attachments",
    response_model=list[MediaAssetResponse],
    summary="List complaint evidence attachments",
    description="Returns all evidence attachments for a customer complaint.",
)
def list_complaint_evidence(
    complaint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """List complaint evidence attachments."""
    return MediaService(db).list_complaint_attachments(current_user, complaint_id)


# ─── ADMIN MEDIA MANAGEMENT ──────────────────────────────────────────────


@router.get(
    "/admin/media",
    response_model=MediaAssetListResponse,
    summary="Admin list all media assets",
    description="**Admin only.** Lists all uploaded media assets across the platform with filtering.",
)
def admin_list_media(
    asset_type: Optional[MediaAssetType] = Query(None),
    owner_type: Optional[str] = Query(None),
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Admin list platform media assets."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permissions required.")
    
    from app.models.media import MediaAsset
    stmt = select(MediaAsset)
    if asset_type:
        stmt = stmt.where(MediaAsset.asset_type == asset_type)
    if owner_type:
        stmt = stmt.where(MediaAsset.owner_type == owner_type)
    stmt = stmt.order_by(MediaAsset.created_at.desc()).offset(offset).limit(limit)
    assets = list(db.scalars(stmt).all())
    
    items = [
        MediaAssetResponse(
            id=a.id,
            owner_id=a.owner_id,
            owner_type=a.owner_type,
            asset_type=a.asset_type,
            cloudinary_asset_id=a.cloudinary_asset_id,
            cloudinary_public_id=a.cloudinary_public_id,
            secure_url=a.secure_url,
            thumbnail_url=MediaService(db).cloudinary.get_thumbnail_url(a.cloudinary_public_id) if a.resource_type == "image" else None,
            resource_type=a.resource_type,
            format=a.format,
            width=a.width,
            height=a.height,
            file_size=a.file_size,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )
        for a in assets
    ]
    return MediaAssetListResponse(total=len(items), items=items)


@router.delete(
    "/admin/media/{asset_id}",
    response_model=StandardMediaResponse,
    summary="Admin delete media asset",
    description="**Admin only.** Deletes a media asset by ID from Cloudinary and DB.",
)
def admin_delete_media(
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Admin delete media asset."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permissions required.")
    
    asset = MediaService(db).crud.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media asset not found.")
    
    MediaService(db).cloudinary.delete_asset(asset.cloudinary_public_id, resource_type=asset.resource_type)
    MediaService(db).crud.delete_media_asset(asset.cloudinary_public_id)
    return StandardMediaResponse(success=True, message="Media asset deleted by administrator.")

