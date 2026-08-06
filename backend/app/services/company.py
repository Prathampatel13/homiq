from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.company import CompanyCRUD
from app.models.auth import User
from app.schemas.company import CompanyProfileResponse, CompanyProfileUpdate


class CompanyService:
    """Business logic for the Company profile.

    Follows the same service-layer pattern as :class:`app.services.customer.CustomerService`
    and :class:`app.services.technician.TechnicianService`.
    """

    def __init__(self, db: Session):
        self.db = db
        self.crud = CompanyCRUD(db)

    def _get_company_or_create(self, user_id: int) -> Any:
        """Get the company profile for a user; create it if it does not exist."""
        company = self.crud.get_by_user_id(user_id)
        if not company:
            company = self.crud.create(user_id)
        return company

    def get_profile(self, current_user: User) -> CompanyProfileResponse:
        company = self._get_company_or_create(current_user.id)
        return self._build_response(current_user, company)

    def update_profile(
        self, current_user: User, payload: CompanyProfileUpdate
    ) -> CompanyProfileResponse:
        company = self._get_company_or_create(current_user.id)

        update_data = payload.model_dump(exclude_unset=True, exclude_none=True)
        full_name = update_data.pop("full_name", None)

        if update_data:
            self.crud.update(company.id, update_data)
            self.db.refresh(company)

        if full_name:
            self.crud.update_user_name(current_user.id, full_name)
            self.db.refresh(company)

        return self._build_response(current_user, company)

    def list_companies(
        self,
        industry: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[CompanyProfileResponse]:
        companies = self.crud.list_companies(
            industry=industry,
            offset=offset,
            limit=limit,
        )
        return [self._build_response(c.user, c) for c in companies]

    def _build_response(
        self, user: User, company: Any
    ) -> CompanyProfileResponse:
        return CompanyProfileResponse(
            id=company.id,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            company_name=company.company_name,
            industry=company.industry,
            description=company.description,
            website=company.website,
            created_at=company.created_at,
        )
