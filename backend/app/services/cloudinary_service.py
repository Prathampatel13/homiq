"""
Reusable Cloudinary Media & Document Service.

Handles deterministic folder routing, strict file validation (MIME, magic bytes, size),
secure uploads, deletion, replacement, and URL optimization.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.cloudinary_config import HAS_CLOUDINARY, is_cloudinary_configured
from app.core.config import settings
from app.models.media import MediaAssetType

if HAS_CLOUDINARY:
    import cloudinary
    import cloudinary.api
    import cloudinary.uploader
    from cloudinary import CloudinaryImage

logger = logging.getLogger("homiq.cloudinary_service")

# ─── VALIDATION CONSTANTS ───────────────────────────────────────────────────

# Disallowed executable extensions
DISALLOWED_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".sh", ".bin", ".msi", ".py", ".pyc",
    ".js", ".php", ".vbs", ".ps1", ".dll", ".scr", ".com", ".jar",
    ".jsp", ".asp", ".aspx", ".cgi", ".pl", ".wsf"
}

# Supported image & document configurations
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
    "image/webp": {".webp"},
}

ALLOWED_DOCUMENT_TYPES = {
    "application/pdf": {".pdf"},
}

# Size limits in bytes
MAX_PROFILE_IMAGE_SIZE = 5 * 1024 * 1024       # 5 MB
MAX_STANDARD_IMAGE_SIZE = 10 * 1024 * 1024     # 10 MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024           # 10 MB

# Document asset types that accept PDFs
DOCUMENT_ASSET_TYPES = {
    MediaAssetType.IDENTITY_DOCUMENT,
    MediaAssetType.TECHNICIAN_CERTIFICATE,
    MediaAssetType.BOOKING_ATTACHMENT,
    MediaAssetType.COMPLAINT_ATTACHMENT,
    MediaAssetType.JOB_RESUME,
    MediaAssetType.JOB_DOCUMENT,
}


class CloudinaryService:
    """Enterprise Cloudinary management service for image & document assets."""

    # ── 1. Deterministic Folder Path Generation ─────────────────────────────

    @staticmethod
    def get_folder_path(asset_type: MediaAssetType, owner_type: str, owner_id: int) -> str:
        """
        Determines the Cloudinary folder structure based on asset type and entity ownership.
        Follows the standard HomiQ hierarchy:
          homiq/users/{user_id}/profile
          homiq/technicians/{technician_id}/profile | certificates | documents | portfolio
          homiq/companies/{company_id}/logo | documents | gallery
          homiq/services/{service_id}/gallery
          homiq/bookings/{booking_id}/before | after | attachments
          homiq/complaints/{complaint_id}/evidence
          homiq/reviews/{review_id}/images
          homiq/jobs/{job_id}/resumes | documents
        """
        ot = owner_type.lower()
        
        if asset_type == MediaAssetType.PROFILE_AVATAR:
            if ot == "technician":
                return f"homiq/technicians/{owner_id}/profile"
            return f"homiq/users/{owner_id}/profile"
            
        elif asset_type == MediaAssetType.COMPANY_LOGO:
            return f"homiq/companies/{owner_id}/logo"
            
        elif asset_type in (MediaAssetType.SERVICE_IMAGE, MediaAssetType.SERVICE_GALLERY):
            return f"homiq/services/{owner_id}/gallery"
            
        elif asset_type == MediaAssetType.TECHNICIAN_PORTFOLIO:
            return f"homiq/technicians/{owner_id}/portfolio"
            
        elif asset_type == MediaAssetType.TECHNICIAN_CERTIFICATE:
            return f"homiq/technicians/{owner_id}/certificates"
            
        elif asset_type == MediaAssetType.IDENTITY_DOCUMENT:
            if ot == "technician":
                return f"homiq/technicians/{owner_id}/documents"
            return f"homiq/users/{owner_id}/documents"
            
        elif asset_type == MediaAssetType.BOOKING_BEFORE:
            return f"homiq/bookings/{owner_id}/before"
            
        elif asset_type == MediaAssetType.BOOKING_AFTER:
            return f"homiq/bookings/{owner_id}/after"
            
        elif asset_type == MediaAssetType.BOOKING_ATTACHMENT:
            return f"homiq/bookings/{owner_id}/attachments"
            
        elif asset_type == MediaAssetType.COMPLAINT_ATTACHMENT:
            return f"homiq/complaints/{owner_id}/evidence"
            
        elif asset_type == MediaAssetType.REVIEW_IMAGE:
            return f"homiq/reviews/{owner_id}/images"
            
        elif asset_type == MediaAssetType.PROPERTY_IMAGE:
            return f"homiq/properties/{owner_id}/images"
            
        elif asset_type == MediaAssetType.JOB_RESUME:
            return f"homiq/jobs/{owner_id}/resumes"
            
        elif asset_type == MediaAssetType.JOB_DOCUMENT:
            return f"homiq/jobs/{owner_id}/documents"
            
        return f"homiq/{ot}s/{owner_id}/{asset_type.value}"

    # ── 2. Comprehensive File Validation ────────────────────────────────────

    @classmethod
    def validate_file(
        cls,
        file: UploadFile,
        asset_type: MediaAssetType,
    ) -> tuple[bytes, str, str]:
        """
        Validates file existence, extension, MIME type, size limit, and magic bytes.
        Returns: (file_bytes, detected_mime_type, file_extension)
        """
        if not file or not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file submission.",
            )

        filename = file.filename.strip()
        _, ext = os.path.splitext(filename.lower())

        # 1. Reject executable extensions
        if ext in DISALLOWED_EXTENSIONS:
            logger.warning("Rejected malicious/executable file extension: %s", ext)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Files with extension '{ext}' are not permitted.",
            )

        # 2. Read content bytes
        try:
            content = file.file.read()
            file.file.seek(0)
        except Exception as exc:
            logger.error("Failed reading upload file bytes: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to read uploaded file.",
            )

        file_size = len(content)
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty (0 bytes).",
            )

        # 3. Determine allowable types & size limits based on asset type
        allows_documents = asset_type in DOCUMENT_ASSET_TYPES
        
        if asset_type == MediaAssetType.PROFILE_AVATAR:
            max_size = MAX_PROFILE_IMAGE_SIZE
            allowed_mime_map = ALLOWED_IMAGE_TYPES
        elif allows_documents:
            max_size = MAX_DOCUMENT_SIZE
            # Allow images + documents
            allowed_mime_map = {**ALLOWED_IMAGE_TYPES, **ALLOWED_DOCUMENT_TYPES}
        else:
            max_size = MAX_STANDARD_IMAGE_SIZE
            allowed_mime_map = ALLOWED_IMAGE_TYPES

        # 4. Check size limit
        if file_size > max_size:
            max_mb = max_size // (1024 * 1024)
            actual_mb = round(file_size / (1024 * 1024), 2)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size ({actual_mb}MB) exceeds maximum permitted size of {max_mb}MB for {asset_type.value}.",
            )

        # 5. Magic byte content verification
        detected_mime: Optional[str] = None
        
        if content.startswith(b"\xff\xd8\xff"):
            detected_mime = "image/jpeg"
        elif content.startswith(b"\x89PNG\r\n\x1a\n"):
            detected_mime = "image/png"
        elif content.startswith(b"RIFF") and len(content) > 12 and content[8:12] == b"WEBP":
            detected_mime = "image/webp"
        elif content.startswith(b"%PDF-"):
            detected_mime = "application/pdf"
        elif file.content_type in allowed_mime_map:
            detected_mime = file.content_type

        if not detected_mime or detected_mime not in allowed_mime_map:
            allowed_names = [k.split("/")[-1].upper() for k in allowed_mime_map.keys()]
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type. Allowed formats for {asset_type.value}: {', '.join(allowed_names)}.",
            )

        # 6. Check extension matches MIME
        valid_exts = allowed_mime_map.get(detected_mime, set())
        if ext and ext not in valid_exts:
            logger.warning("MIME/Extension mismatch: MIME=%s, ext=%s", detected_mime, ext)
            # Normalise ext from detected mime if valid
            ext = list(valid_exts)[0]

        return content, detected_mime, ext

    # ── 3. Core Upload & Document Processing ────────────────────────────────

    def upload_file(
        self,
        file: UploadFile,
        owner_id: int,
        owner_type: str,
        asset_type: MediaAssetType,
        public_id_override: Optional[str] = None,
        transformations: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Validates, prepares, and uploads a file/image to Cloudinary in the deterministic folder.
        Returns cleaned internal metadata dictionary.
        """
        content, mime_type, ext = self.validate_file(file, asset_type)
        folder = self.get_folder_path(asset_type, owner_type, owner_id)
        
        resource_type = "raw" if mime_type == "application/pdf" else "image"
        pid = public_id_override or f"{folder}/{uuid4().hex[:12]}"
        clean_format = ext.lstrip(".") or ("pdf" if resource_type == "raw" else "png")

        if is_cloudinary_configured() and HAS_CLOUDINARY:
            try:
                upload_options: dict[str, Any] = {
                    "folder": folder,
                    "resource_type": resource_type,
                    "public_id": pid.split("/")[-1],
                    "overwrite": True,
                }
                if transformations and resource_type == "image":
                    upload_options["transformation"] = transformations

                file.file.seek(0)
                result = cloudinary.uploader.upload(file.file, **upload_options)

                secure_url = result.get("secure_url") or result.get("url") or ""
                public_id = result.get("public_id", pid)
                asset_id = result.get("asset_id")

                return {
                    "cloudinary_asset_id": asset_id,
                    "cloudinary_public_id": public_id,
                    "secure_url": secure_url,
                    "resource_type": resource_type,
                    "format": result.get("format", clean_format),
                    "width": result.get("width"),
                    "height": result.get("height"),
                    "file_size": result.get("bytes", len(content)),
                    "folder": folder,
                }
            except Exception as exc:
                logger.error("Cloudinary upload failed: %s", exc)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Cloudinary upload service failed to process the asset.",
                )

        # Fallback Mock / Offline Mode
        cloud = settings.CLOUDINARY_CLOUD_NAME or "homiq-cloud"
        mock_url = f"https://res.cloudinary.com/{cloud}/{resource_type}/upload/v1/{pid}.{clean_format}"
        
        return {
            "cloudinary_asset_id": f"asset_{uuid4().hex[:10]}",
            "cloudinary_public_id": pid,
            "secure_url": mock_url,
            "resource_type": resource_type,
            "format": clean_format,
            "width": 800 if resource_type == "image" else None,
            "height": 600 if resource_type == "image" else None,
            "file_size": len(content),
            "folder": folder,
        }

    # ── 4. Asset Deletion & Replacement ─────────────────────────────────────

    def delete_asset(self, cloudinary_public_id: str, resource_type: str = "image") -> bool:
        """
        Deletes an asset from Cloudinary by public ID.
        """
        if not cloudinary_public_id:
            return False

        if is_cloudinary_configured() and HAS_CLOUDINARY:
            try:
                result = cloudinary.uploader.destroy(
                    cloudinary_public_id,
                    resource_type=resource_type,
                    invalidate=True,
                )
                return result.get("result") in ("ok", "not found")
            except Exception as exc:
                logger.warning("Cloudinary delete error for '%s': %s", cloudinary_public_id, exc)
                return False
        return True

    def replace_asset(
        self,
        old_public_id: str,
        file: UploadFile,
        owner_id: int,
        owner_type: str,
        asset_type: MediaAssetType,
        resource_type: str = "image",
    ) -> dict[str, Any]:
        """
        Replaces an existing Cloudinary asset with a newly uploaded file.
        """
        if old_public_id:
            self.delete_asset(old_public_id, resource_type=resource_type)
        return self.upload_file(file, owner_id=owner_id, owner_type=owner_type, asset_type=asset_type)

    # ── 5. URL Optimization & Transformations ───────────────────────────────

    def get_optimized_url(
        self,
        public_id: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        crop: str = "fill",
        quality: str = "auto",
        fetch_format: str = "auto",
        gravity: str = "auto",
    ) -> str:
        """
        Generates an optimized Cloudinary transformation URL.
        """
        if not public_id:
            return ""

        cloud = settings.CLOUDINARY_CLOUD_NAME or "homiq-cloud"

        if is_cloudinary_configured() and HAS_CLOUDINARY:
            try:
                transformation: dict[str, Any] = {
                    "quality": quality,
                    "fetch_format": fetch_format,
                }
                if width:
                    transformation["width"] = width
                if height:
                    transformation["height"] = height
                if crop:
                    transformation["crop"] = crop
                if gravity:
                    transformation["gravity"] = gravity

                return CloudinaryImage(public_id).build_url(**transformation)
            except Exception as exc:
                logger.warning("Error generating Cloudinary transformation: %s", exc)

        transform_params = [f"q_{quality}", f"f_{fetch_format}"]
        if width:
            transform_params.append(f"w_{width}")
        if height:
            transform_params.append(f"h_{height}")
        if crop:
            transform_params.append(f"c_{crop}")
        if gravity:
            transform_params.append(f"g_{gravity}")

        t_str = ",".join(transform_params)
        return f"https://res.cloudinary.com/{cloud}/image/upload/{t_str}/{public_id}"

    def get_thumbnail_url(self, public_id: str, width: int = 200, height: int = 200) -> str:
        """Helper to generate standard 200x200 crop thumbnail."""
        return self.get_optimized_url(
            public_id=public_id,
            width=width,
            height=height,
            crop="fill",
            gravity="auto",
        )


cloudinary_service = CloudinaryService()
