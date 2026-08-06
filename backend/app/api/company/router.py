"""
Company profile management endpoints.

Provides:
- Company profile retrieval and update (JWT-protected, company role required)
- Public listing of companies (no authentication)
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.security.deps import get_current_company
from app.schemas.company import CompanyProfileResponse, CompanyProfileUpdate
from app.services.company import CompanyService

router = APIRouter(prefix="/company", tags=["Company"])


@router.get(
    "/profile",
    response_model=CompanyProfileResponse,
    summary="Get company profile",
    description="Returns the authenticated company's profile information.",
)
def get_profile(
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Any:
    """Fetch the authenticated company's profile."""
    return CompanyService(db).get_profile(current_user)


@router.put(
    "/profile",
    response_model=CompanyProfileResponse,
    summary="Update company profile",
    description="Update company fields such as name, industry, description, and website. Only provided fields are updated.",
)
def update_profile(
    payload: CompanyProfileUpdate,
    current_user: User = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Any:
    """Update the company's profile. Omitting a field leaves it unchanged."""
    return CompanyService(db).update_profile(current_user, payload)


@router.get(
    "/",
    response_model=list[CompanyProfileResponse],
    summary="List companies",
    description="Returns a paginated list of companies. Optionally filter by industry. Public endpoint.",
)
def list_companies(
    industry: str | None = None,
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> Any:
    """List all companies (public metadata)."""
    return CompanyService(db).list_companies(
        industry=industry,
        offset=offset,
        limit=limit,
    )
