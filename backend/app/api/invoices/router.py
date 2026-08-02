"""
Invoice management endpoints.

Admin: Full CRUD for invoices.
Customers: View their own invoices.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.auth import User
from app.models.invoices import InvoiceStatus
from app.security.deps import get_current_user
from app.schemas.invoices import (
    InvoiceCreate,
    InvoiceListResponse,
    InvoiceResponse,
    InvoiceUpdate,
)
from app.services.invoice import InvoiceService

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post(
    "/",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an invoice (Admin)",
    description="**Admin only.** Creates a new invoice for a booking with pricing details.",
)
def create_invoice(
    payload: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create an invoice for a booking. Admin access required."""
    return InvoiceService(db).create_invoice(current_user, payload)


@router.get(
    "/",
    response_model=InvoiceListResponse,
    summary="List invoices",
    description="Returns a paginated list of invoices. Admins see all; customers see their own.",
)
def list_invoices(
    status_filter: Optional[InvoiceStatus] = None,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """List invoices with optional status filter, scoped to user role."""
    return InvoiceService(db).list_invoices(
        current_user,
        status=status_filter,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Get invoice by ID",
    description="Returns the details of a specific invoice by its ID.",
)
def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get an invoice by its ID."""
    return InvoiceService(db).get_invoice(current_user, invoice_id)


@router.get(
    "/number/{invoice_number}",
    response_model=InvoiceResponse,
    summary="Get invoice by number",
    description="Returns invoice details by its unique invoice number.",
)
def get_invoice_by_number(
    invoice_number: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get an invoice by its invoice number."""
    return InvoiceService(db).get_invoice_by_number(invoice_number)


@router.put(
    "/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Update an invoice (Admin)",
    description="**Admin only.** Updates one or more fields of an existing invoice.",
)
def update_invoice(
    invoice_id: int,
    payload: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Update an invoice by ID. Admin access required."""
    return InvoiceService(db).update_invoice(current_user, invoice_id, payload)


@router.post(
    "/{invoice_id}/issue",
    response_model=InvoiceResponse,
    summary="Issue an invoice (Admin)",
    description="**Admin only.** Transitions an invoice from 'draft' to 'issued' status.",
)
def issue_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Issue an invoice (draft -> issued). Admin access required."""
    return InvoiceService(db).issue_invoice(current_user, invoice_id)


@router.delete(
    "/{invoice_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an invoice (Admin)",
    description="**Admin only.** Deletes an invoice by its ID.",
)
def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """Delete an invoice by ID. Admin access required."""
    return InvoiceService(db).delete_invoice(current_user, invoice_id)

