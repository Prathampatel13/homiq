from typing import Any, Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.auth import User
from app.models.users import Technician


class TechnicianCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[Technician]:
        return self.db.scalar(select(Technician).where(Technician.user_id == user_id))

    def get_by_technician_id(self, technician_id: int) -> Optional[Technician]:
        return self.db.get(Technician, technician_id)

    def create(self, user_id: int) -> Technician:
        technician = Technician(user_id=user_id)
        self.db.add(technician)
        self.db.commit()
        self.db.refresh(technician)
        return technician

    def update(self, technician_id: int, data: dict[str, Any]) -> Optional[Technician]:
        if not data:
            return self.get_by_technician_id(technician_id)

        stmt = (
            update(Technician)
            .where(Technician.id == technician_id)
            .values(**data)
            .returning(Technician)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.scalar_one_or_none()

    def delete(self, technician_id: int) -> bool:
        technician = self.get_by_technician_id(technician_id)
        if not technician:
            return False
        self.db.delete(technician)
        self.db.commit()
        return True

    def list_technicians(
        self,
        specialization: Optional[str] = None,
        availability: Optional[bool] = None,
        online: Optional[bool] = None,
    ) -> list[Technician]:
        stmt = select(Technician)
        if specialization:
            stmt = stmt.where(Technician.specialization.ilike(f"%{specialization}%"))
        if availability is not None:
            stmt = stmt.where(Technician.availability == availability)
        if online is not None:
            stmt = stmt.where(Technician.is_online == online)

        result = self.db.execute(
            stmt.order_by(Technician.rating.desc(), Technician.reviews_count.desc())
        )
        return list(result.scalars().all())

    def update_user_name(self, user_id: int, full_name: str) -> None:
        user = self.db.get(User, user_id)
        if user:
            user.full_name = full_name
            self.db.commit()
