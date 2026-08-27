from typing import Any, Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.auth import User
from app.models.users import Company


class CompanyCRUD:
    """Repository-style CRUD operations for the :class:`Company` profile.

    Mirrors the pattern of :class:`app.crud.customer.CustomerCRUD` and
    :class:`app.crud.technician.TechnicianCRUD`.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[Company]:
        return self.db.scalar(
            select(Company).where(Company.user_id == user_id)
        )

    def get_by_company_id(self, company_id: int) -> Optional[Company]:
        return self.db.get(Company, company_id)

    def create(self, user_id: int) -> Company:
        company = Company(user_id=user_id)
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def update(
        self, company_id: int, data: dict[str, Any]
    ) -> Optional[Company]:
        if not data:
            return self.get_by_company_id(company_id)

        stmt = (
            update(Company)
            .where(Company.id == company_id)
            .values(**data)
            .returning(Company)
        )
        result = self.db.execute(stmt)
        item = result.scalar_one_or_none()
        self.db.commit()
        return item

    def delete(self, company_id: int) -> bool:
        company = self.get_by_company_id(company_id)
        if not company:
            return False
        self.db.delete(company)
        self.db.commit()
        return True

    def list_companies(
        self,
        industry: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Company]:
        stmt = select(Company)
        if industry:
            stmt = stmt.where(Company.industry.ilike(f"%{industry}%"))
        stmt = stmt.order_by(Company.company_name.asc()).offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def update_user_name(self, user_id: int, full_name: str) -> None:
        user = self.db.get(User, user_id)
        if user:
            user.full_name = full_name
            self.db.commit()
