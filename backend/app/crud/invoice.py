from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.invoices import Invoice, InvoiceStatus


class InvoiceCRUD:
    def __init__(self, db: Session):
        self.db = db

    # ── Create ─────────────────────────────────────────────────────────

    def create(self, data: dict) -> Invoice:
        invoice = Invoice(**data)
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    # ── Get ────────────────────────────────────────────────────────────

    def get(self, invoice_id: int) -> Optional[Invoice]:
        return self.db.get(Invoice, invoice_id)

    def get_by_invoice_number(self, invoice_number: str) -> Optional[Invoice]:
        stmt = select(Invoice).where(Invoice.invoice_number == invoice_number)
        return self.db.scalar(stmt)

    def get_by_booking(self, booking_id: int) -> Optional[Invoice]:
        stmt = select(Invoice).where(Invoice.booking_id == booking_id)
        return self.db.scalar(stmt)

    # ── List ───────────────────────────────────────────────────────────

    def list_invoices(
        self,
        customer_id: Optional[int] = None,
        status: Optional[InvoiceStatus] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Invoice]:
        stmt = select(Invoice).order_by(Invoice.created_at.desc())
        if customer_id is not None:
            stmt = stmt.where(Invoice.customer_id == customer_id)
        if status is not None:
            stmt = stmt.where(Invoice.status == status)
        stmt = stmt.offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_invoices(
        self,
        customer_id: Optional[int] = None,
        status: Optional[InvoiceStatus] = None,
    ) -> int:
        stmt = select(func.count(Invoice.id))
        if customer_id is not None:
            stmt = stmt.where(Invoice.customer_id == customer_id)
        if status is not None:
            stmt = stmt.where(Invoice.status == status)
        return self.db.scalar(stmt) or 0

    # ── Update ─────────────────────────────────────────────────────────

    def update(self, invoice_id: int, data: dict) -> Optional[Invoice]:
        invoice = self.get(invoice_id)
        if not invoice:
            return None
        for key, value in data.items():
            setattr(invoice, key, value)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    # ── Status Transitions ─────────────────────────────────────────────

    def mark_issued(self, invoice: Invoice) -> Invoice:
        invoice.status = InvoiceStatus.ISSUED
        invoice.issued_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def mark_paid(self, invoice: Invoice, amount_paid: float) -> Invoice:
        invoice.amount_paid = amount_paid
        invoice.amount_due = max(0.0, invoice.total_amount - amount_paid)
        invoice.paid_at = datetime.now(timezone.utc)
        if invoice.amount_due <= 0:
            invoice.status = InvoiceStatus.PAID
        else:
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def mark_cancelled(self, invoice: Invoice) -> Invoice:
        invoice.status = InvoiceStatus.CANCELLED
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def mark_refunded(self, invoice: Invoice) -> Invoice:
        invoice.status = InvoiceStatus.REFUNDED
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    # ── Delete ─────────────────────────────────────────────────────────

    def delete(self, invoice_id: int) -> bool:
        invoice = self.get(invoice_id)
        if not invoice:
            return False
        self.db.delete(invoice)
        self.db.commit()
        return True

    # ── Revenue Aggregations ───────────────────────────────────────────

    def total_revenue(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> float:
        stmt = select(func.coalesce(func.sum(Invoice.total_amount), 0)).where(
            Invoice.status.in_([InvoiceStatus.PAID, InvoiceStatus.PARTIALLY_PAID])
        )
        if start_date:
            stmt = stmt.where(Invoice.paid_at >= start_date)
        if end_date:
            stmt = stmt.where(Invoice.paid_at <= end_date)
        return float(self.db.scalar(stmt) or 0.0)

    def revenue_by_month(self, year: int) -> list[dict]:
        """Returns monthly revenue breakdown for a given year."""
        import calendar
        from sqlalchemy import extract

        result = []
        for month in range(1, 13):
            stmt = select(func.coalesce(func.sum(Invoice.total_amount), 0)).where(
                Invoice.status.in_([InvoiceStatus.PAID, InvoiceStatus.PARTIALLY_PAID]),
                extract("year", Invoice.paid_at) == year,
                extract("month", Invoice.paid_at) == month,
            )
            revenue = float(self.db.scalar(stmt) or 0.0)
            result.append({"month": calendar.month_name[month], "revenue": revenue})
        return result

    def revenue_by_service(self) -> list[dict]:
        """Returns revenue grouped by service (via booking join)."""
        from app.models.bookings import Booking
        from app.models.services import Service
        from sqlalchemy import join

        stmt = (
            select(
                Service.name,
                func.coalesce(func.sum(Invoice.total_amount), 0).label("revenue"),
                func.count(Invoice.id).label("count"),
            )
            .select_from(
                join(Invoice, Booking, Invoice.booking_id == Booking.id)
                .join(Service, Booking.service_id == Service.id)
            )
            .where(
                Invoice.status.in_([InvoiceStatus.PAID, InvoiceStatus.PARTIALLY_PAID])
            )
            .group_by(Service.name)
            .order_by(func.sum(Invoice.total_amount).desc())
        )
        results = self.db.execute(stmt).all()
        return [
            {"service_name": row[0], "revenue": float(row[1]), "count": row[2]}
            for row in results
        ]

    def generate_invoice_number(self) -> str:
        """Generate a unique invoice number: INV-YYYYMMDD-XXXXX"""
        today = datetime.now(timezone.utc)
        count = self.db.scalar(
            select(func.count(Invoice.id)).where(
                func.date(Invoice.created_at) == today.date()
            )
        ) or 0
        seq = int(count) + 1
        return f"INV-{today.strftime('%Y%m%d')}-{seq:05d}"

