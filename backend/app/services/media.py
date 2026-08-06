from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session

from app.crud.media import MediaCRUD
from app.crud.customer import CustomerCRUD
from app.crud.technician import TechnicianCRUD
from app.integrations.cloudinary import CloudinaryClient
from app.models.auth import User
from app.schemas.media import (
    DocumentApprovalPayload,
    DocumentStatusEnum,
    DocumentTypeEnum,
    MediaFolderEnum,
    MediaResponse,
    TechnicianDocumentResponse,
)

# In-memory document verification registry
DOCUMENT_STORE: dict[str, dict[str, Any]] = {}


class MediaService:
    """Service layer for Cloudinary Media & Document Management."""

    def __init__(self, db: Session):
        self.db = db
        self.crud = MediaCRUD(db)
        self.customer_crud = CustomerCRUD(db)
        self.technician_crud = TechnicianCRUD(db)
        self.cloudinary = CloudinaryClient()

    # ── Upload & Media Operations ──────────────────────────────────────────

    def upload_file(
        self,
        current_user: User,
        file: UploadFile,
        folder: str = "homiq",
    ) -> MediaResponse:
        """Upload file to Cloudinary and return optimized URL and thumbnail."""
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file submission.",
            )

        # Upload via CloudinaryClient
        res = self.cloudinary.upload_image(file=file, folder=folder)

        public_id = res.get("public_id", f"{folder}/{uuid4().hex}")
        secure_url = res.get("secure_url") or res.get("url") or ""

        # Thumbnail generation (200x200 crop fill)
        thumbnail_url = self.cloudinary.get_image_url(
            public_id=public_id,
            width=200,
            height=200,
            crop="fill",
        )

        # Automatically update profile image if uploaded under profiles folder
        if "profiles" in folder:
            if current_user.role_id == 1:  # Customer
                cust = self.customer_crud.get_by_user_id(current_user.id)
                if cust:
                    self.crud.update_customer_profile_image(cust.id, secure_url)
            elif current_user.role_id == 2:  # Technician
                tech = self.technician_crud.get_by_user_id(current_user.id)
                if tech:
                    self.crud.update_technician_profile_image(tech.id, secure_url)

        return MediaResponse(
            public_id=public_id,
            url=res.get("url", secure_url),
            secure_url=secure_url,
            thumbnail_url=thumbnail_url,
            format=res.get("format", "png"),
            width=res.get("width", 0),
            height=res.get("height", 0),
            bytes=res.get("bytes", 0),
            folder=folder,
            uploaded_at=datetime.now(timezone.utc),
        )

    def get_media_details(self, public_id: str) -> MediaResponse:
        """Get Cloudinary media details and optimized URLs."""
        if not public_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid media public ID.",
            )

        url = self.cloudinary.get_image_url(public_id)
        thumbnail_url = self.cloudinary.get_image_url(
            public_id=public_id,
            width=200,
            height=200,
            crop="fill",
        )

        return MediaResponse(
            public_id=public_id,
            url=url,
            secure_url=url,
            thumbnail_url=thumbnail_url,
            format="png",
            folder="homiq",
            uploaded_at=datetime.now(timezone.utc),
        )

    def delete_media(self, current_user: User, public_id: str) -> dict[str, str]:
        """Delete file from Cloudinary."""
        if not public_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Public ID required for deletion.",
            )

        success = self.cloudinary.delete_image(public_id)
        return {"message": "Media asset deleted successfully." if success else "Media deletion requested."}

    def replace_media(
        self,
        current_user: User,
        public_id: str,
        file: UploadFile,
        folder: str = "homiq",
    ) -> MediaResponse:
        """Replace existing Cloudinary asset with new file."""
        if public_id:
            try:
                self.cloudinary.delete_image(public_id)
            except Exception:
                pass

        return self.upload_file(current_user, file, folder=folder)

    # ── Technician Verification Documents ────────────────────────────────

    def upload_technician_document(
        self,
        current_user: User,
        doc_type: DocumentTypeEnum,
        file: UploadFile,
    ) -> TechnicianDocumentResponse:
        """Upload technician verification document (Aadhaar, PAN, License, Certificate)."""
        tech = self.technician_crud.get_by_user_id(current_user.id)
        if not tech:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician profile not found.",
            )

        # Upload document to technician_docs folder
        res = self.upload_file(current_user, file, folder=MediaFolderEnum.TECHNICIAN_DOCS.value)

        doc_id = f"doc_{uuid4().hex[:8]}"
        doc_record = {
            "id": doc_id,
            "technician_id": tech.id,
            "doc_type": doc_type,
            "url": res.secure_url,
            "public_id": res.public_id,
            "status": DocumentStatusEnum.PENDING,
            "rejection_reason": None,
            "uploaded_at": datetime.now(timezone.utc),
        }
        DOCUMENT_STORE[doc_id] = doc_record

        # Update government_id_image link on technician record
        self.crud.update_technician_government_id(tech.id, res.secure_url)

        return TechnicianDocumentResponse.model_validate(doc_record)

    def get_technician_documents(self, current_user: User) -> list[TechnicianDocumentResponse]:
        """List uploaded verification documents for current technician."""
        tech = self.technician_crud.get_by_user_id(current_user.id)
        if not tech and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technician profile not found.",
            )

        tech_id = tech.id if tech else None
        docs = [
            TechnicianDocumentResponse.model_validate(doc)
            for doc in DOCUMENT_STORE.values()
            if tech_id is None or doc["technician_id"] == tech_id
        ]
        return docs

    def approve_technician_document(self, current_user: User, doc_id: str) -> TechnicianDocumentResponse:
        """Admin approve technician verification document."""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can approve documents.",
            )

        doc = DOCUMENT_STORE.get(doc_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        doc["status"] = DocumentStatusEnum.APPROVED
        doc["rejection_reason"] = None
        return TechnicianDocumentResponse.model_validate(doc)

    def reject_technician_document(
        self,
        current_user: User,
        doc_id: str,
        reason: Optional[str] = "Document illegible or invalid.",
    ) -> TechnicianDocumentResponse:
        """Admin reject technician verification document."""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can reject documents.",
            )

        doc = DOCUMENT_STORE.get(doc_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        doc["status"] = DocumentStatusEnum.REJECTED
        doc["rejection_reason"] = reason
        return TechnicianDocumentResponse.model_validate(doc)
