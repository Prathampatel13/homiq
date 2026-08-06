"""
Cloudinary Media & Document Management endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_user
from app.schemas.media import (
    DocumentApprovalPayload,
    DocumentTypeEnum,
    MediaResponse,
    TechnicianDocumentResponse,
)
from app.services.media import MediaService

router = APIRouter(tags=["Media & Documents"])


@router.post(
    "/media/upload",
    response_model=MediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload media asset",
    description="Uploads an image or file to Cloudinary with automatic optimization and thumbnail generation.",
)
def upload_media(
    file: UploadFile = File(...),
    folder: str = Form("homiq"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Upload media file to Cloudinary."""
    return MediaService(db).upload_file(current_user, file=file, folder=folder)


@router.get(
    "/media/{public_id:path}",
    response_model=MediaResponse,
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
    description="Deletes a media asset from Cloudinary by its public ID.",
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
    response_model=MediaResponse,
    summary="Replace media asset",
    description="Replaces an existing Cloudinary asset with a newly uploaded file.",
)
def replace_media(
    public_id: str,
    file: UploadFile = File(...),
    folder: str = Form("homiq"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Replace media asset."""
    return MediaService(db).replace_media(current_user, public_id=public_id, file=file, folder=folder)


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
