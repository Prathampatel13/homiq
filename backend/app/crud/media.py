from __future__ import annotations

from typing import Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, update

from app.models.users import Customer, Technician
from app.schemas.media import DocumentStatusEnum, DocumentTypeEnum


class MediaCRUD:
    """CRUD operations for Media & Technician Document Management."""

    def __init__(self, db: Session):
        self.db = db

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
