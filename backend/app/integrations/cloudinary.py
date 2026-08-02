"""
Cloudinary integration for image and file hosting.

Provides a client wrapper for:
- Uploading images (profile, service, government ID)
- Generating optimized URLs
- Deleting assets
- Image transformations
"""

from __future__ import annotations

import os
from typing import Any, Optional
from uuid import uuid4

import cloudinary
import cloudinary.api
import cloudinary.uploader
from fastapi import HTTPException, status, UploadFile

from app.core.config import settings


class CloudinaryClient:
    """Singleton-style Cloudinary client wrapper."""

    _instance: Optional["CloudinaryClient"] = None
    _initialized: bool = False

    # Allowed image MIME types
    ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

    def __new__(cls) -> "CloudinaryClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True,
            )
            self._initialized = True

    def upload_image(
        self,
        file: UploadFile,
        folder: str = "homiq",
        public_id: Optional[str] = None,
        transformation: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Upload an image to Cloudinary.

        Args:
            file: The uploaded file.
            folder: Cloudinary folder to store the image.
            public_id: Optional public ID (auto-generated if not provided).
            transformation: Optional image transformation parameters.

        Returns:
            dict: Upload result with url, public_id, secure_url, etc.

        Raises:
            HTTPException: If file type/size validation fails or upload fails.
        """
        # Validate file type
        if file.content_type not in self.ALLOWED_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type '{file.content_type}'. Allowed: {', '.join(self.ALLOWED_TYPES)}",
            )

        # Validate file size
        contents = file.file.read()
        if len(contents) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 5 MB limit.",
            )
        file.file.seek(0)

        try:
            upload_options: dict[str, Any] = {
                "folder": folder,
                "resource_type": "image",
            }
            if public_id:
                upload_options["public_id"] = public_id
            if transformation:
                upload_options["transformation"] = transformation

            result = cloudinary.uploader.upload(file.file, **upload_options)
            return {
                "url": result.get("url", ""),
                "secure_url": result.get("secure_url", ""),
                "public_id": result.get("public_id", ""),
                "format": result.get("format", ""),
                "width": result.get("width", 0),
                "height": result.get("height", 0),
                "bytes": result.get("bytes", 0),
            }
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Cloudinary upload failed: {exc}",
            )

    def delete_image(self, public_id: str) -> bool:
        """
        Delete an image from Cloudinary.

        Args:
            public_id: The public ID of the image to delete.

        Returns:
            bool: True if deletion was successful.
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Cloudinary deletion failed: {exc}",
            )

    def get_image_url(
        self,
        public_id: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        crop: str = "fill",
        quality: str = "auto",
        fetch_format: str = "auto",
    ) -> str:
        """
        Generate an optimized Cloudinary URL for an image.

        Args:
            public_id: The public ID of the image.
            width: Desired width (optional).
            height: Desired height (optional).
            crop: Crop mode (default: fill).
            quality: Image quality (default: auto).
            fetch_format: Image format (default: auto).

        Returns:
            str: Optimized Cloudinary URL.
        """
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

        return cloudinary.CloudinaryImage(public_id).build_url(**transformation)

    def list_images(self, folder: str = "homiq", max_results: int = 50) -> list[dict[str, Any]]:
        """
        List all images in a Cloudinary folder.

        Args:
            folder: The folder to list.
            max_results: Maximum number of results.

        Returns:
            list[dict]: List of image resources.
        """
        try:
            result = cloudinary.api.resources(
                type="upload",
                prefix=folder,
                max_results=max_results,
            )
            return result.get("resources", [])
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to list Cloudinary resources: {exc}",
            )

