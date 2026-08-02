from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.invoice import InvoiceCRUD
from app.crud.customer import CustomerCRUD
from app.models.auth import User
from app.models.invoices import InvoiceStatus
from app.schemas.invoices import (
    InvoiceCreate,
    InvoiceListResponse,
    InvoiceResponse,
    InvoiceUpdate,
)


class InvoiceService:
    """Service layer for invoice operations."""

    def __init__(self, db: Session):
        self.db = db
        self.crud = InvoiceCRUD(db)
        self.customer_crud = CustomerCRUD(db)

    def _get_customer_id(self, current_user: User) -> int:
        customer = self.customer_crud.get_by_user_id(current_user.id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found.",
            )
        return customer.id

    # ── Create ─────────────────────────────────────────────────────────

    def create_invoice(self, current_user: User, payload: InvoiceCreate) -> InvoiceResponse:
        """Create a new invoice. Admin only."""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required.",
            )

        # Check if invoice already exists for this booking
        existing = self.crud.get_by_booking(payload.booking_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invoice already exists for this booking.",
            )

        from app.crud.booking import BookingCRUD
        booking_crud = BookingCRUD(self.db)
        booking = booking_crud.get_booking(payload.booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )

        data = payload.model_dump()
        data["invoice_number"] = self.crud.generate_invoice_number()
        data["customer_id"] = booking.customer_id
        data["tax_amount"] = round(payload.subtotal * payload.tax_percentage / 100.0, 2)
        data["amount_due"] = payload.total_amount - payload.amount_paid
        data["status"] = InvoiceStatus.DRAFT

        invoice = self.crud.create(data)
        return InvoiceResponse.model_validate(invoice)

    # ── Get ────────────────────────────────────────────────────────────

    def get_invoice(self, current_user: User, invoice_id: int) -> InvoiceResponse:
        """Get an invoice by ID."""
        invoice = self.crud.get(invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found.",
            )

        is_owner = invoice.customer_id == self._get_customer_id(current_user) if not current_user.is_superuser else False
        if not (current_user.is_superuser or is_owner):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this invoice.",
            )

        return InvoiceResponse.model_validate(invoice)

    def get_invoice_by_number(self, invoice_number: str) -> InvoiceResponse:
        """Get an invoice by invoice number."""
        invoice = self.crud.get_by_invoice_number(invoice_number)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found.",
            )
        return InvoiceResponse.model_validate(invoice)

    # ── List ───────────────────────────────────────────────────────────

    def list_invoices(
        self,
        current_user: User,
        status: Optional[InvoiceStatus] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> InvoiceListResponse:
        """List invoices scoped to user role."""
        if current_user.is_superuser:
            invoices = self.crud.list_invoices(
                status=status, offset=offset, limit=limit
            )
            total = self.crud.count_invoices(status=status)
        else:
            customer_id = self._get_customer_id(current_user)
            invoices = self.crud.list_invoices(
                customer_id=customer_id,
                status=status,
                offset=offset,
                limit=limit,
            )
            total = self.crud.count_invoices(
                customer_id=customer_id,
                status=status,
            )

        return InvoiceListResponse(
            items=[InvoiceResponse.model_validate(i) for i in invoices],
            total=total,
        )

    # ── Update ─────────────────────────────────────────────────────────

    def update_invoice(
        self, current_user: User, invoice_id: int, payload: InvoiceUpdate
    ) -> InvoiceResponse:
        """Update an invoice. Admin only."""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required.",
            )

        invoice = self.crud.get(invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found.",
            )

        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update.",
            )

        updated = self.crud.update(invoice_id, data)
        return InvoiceResponse.model_validate(updated)

    # ── Issue ──────────────────────────────────────────────────────────

    def issue_invoice(self, current_user: User, invoice_id: int) -> InvoiceResponse:
        """Issue an invoice (transition from draft to issued). Admin only."""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required.",
            )

        invoice = self.crud.get(invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found.",
            )

        if invoice.status != InvoiceStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot issue invoice with status '{invoice.status.value}'.",
            )

        updated = self.crud.mark_issued(invoice)
        return InvoiceResponse.model_validate(updated)

    # ── Delete ─────────────────────────────────────────────────────────

    def delete_invoice(self, current_user: User, invoice_id: int) -> dict[str, str]:
        """Delete an invoice. Admin only."""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required.",
            )

        deleted = self.crud.delete(invoice_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found.",
            )
        return {"message": "Invoice deleted successfully."}

