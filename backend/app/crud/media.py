"""
CRUD operations for MediaAsset and Profile/Verification records.
"""

from __future__ import annotations

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.media import MediaAsset, MediaAssetType
from app.models.users import Customer, Technician


class MediaCRUD:
    """CRUD operations for centralized Media Assets & Profile References."""

    def __init__(self, db: Session):
        self.db = db

    # ── MediaAsset DB Records ────────────────────────────────────────────────

    def create_media_asset(
        self,
        owner_id: int,
        owner_type: str,
        asset_type: MediaAssetType,
        cloudinary_public_id: str,
        secure_url: str,
        resource_type: str = "image",
        format: str = "png",
        width: Optional[int] = None,
        height: Optional[int] = None,
        file_size: int = 0,
        cloudinary_asset_id: Optional[str] = None,
    ) -> MediaAsset:
        """Create and persist a new MediaAsset record."""
        asset = MediaAsset(
            owner_id=owner_id,
            owner_type=owner_type,
            asset_type=asset_type,
            cloudinary_asset_id=cloudinary_asset_id,
            cloudinary_public_id=cloudinary_public_id,
            secure_url=secure_url,
            resource_type=resource_type,
            format=format,
            width=width,
            height=height,
            file_size=file_size,
        )
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def get_by_id(self, asset_id: int) -> Optional[MediaAsset]:
        """Fetch media asset by primary key ID."""
        return self.db.get(MediaAsset, asset_id)

    def get_by_public_id(self, public_id: str) -> Optional[MediaAsset]:
        """Fetch media asset by Cloudinary public ID."""
        stmt = select(MediaAsset).where(MediaAsset.cloudinary_public_id == public_id)
        return self.db.scalars(stmt).first()

    def get_assets_by_owner(
        self,
        owner_id: int,
        owner_type: str,
        asset_type: Optional[MediaAssetType] = None,
    ) -> list[MediaAsset]:
        """Fetch all media assets belonging to an entity, optionally filtered by asset type."""
        stmt = select(MediaAsset).where(
            MediaAsset.owner_id == owner_id,
            MediaAsset.owner_type == owner_type,
        )
        if asset_type:
            stmt = stmt.where(MediaAsset.asset_type == asset_type)
        stmt = stmt.order_by(MediaAsset.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def delete_media_asset(self, public_id: str) -> bool:
        """Delete a media asset record from the database."""
        asset = self.get_by_public_id(public_id)
        if not asset:
            return False
        self.db.delete(asset)
        self.db.commit()
        return True

    # ── User Profile & Government ID Convenience Links ───────────────────────

    def update_customer_profile_image(self, customer_id: int, image_url: str) -> Optional[Customer]:
        """Update customer profile image URL."""
        customer = self.db.get(Customer, customer_id)
        if not customer:
            return None
        customer.profile_image = image_url
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def update_technician_profile_image(self, technician_id: int, image_url: str) -> Optional[Technician]:
        """Update technician profile image URL."""
        technician = self.db.get(Technician, technician_id)
        if not technician:
            return None
        technician.profile_image = image_url
        self.db.commit()
        self.db.refresh(technician)
        return technician

    def update_technician_government_id(self, technician_id: int, document_url: str) -> Optional[Technician]:
        """Update technician government ID document URL."""
        technician = self.db.get(Technician, technician_id)
        if not technician:
            return None
        technician.government_id_image = document_url
        self.db.commit()
        self.db.refresh(technician)
        return technician

    def delete_customer_profile_image(self, customer_id: int) -> bool:
        """Clear customer profile image."""
        customer = self.db.get(Customer, customer_id)
        if not customer:
            return False
        customer.profile_image = None
        self.db.commit()
        return True

    def delete_technician_profile_image(self, technician_id: int) -> bool:
        """Clear technician profile image."""
        technician = self.db.get(Technician, technician_id)
        if not technician:
            return False
        technician.profile_image = None
        self.db.commit()
        return True
