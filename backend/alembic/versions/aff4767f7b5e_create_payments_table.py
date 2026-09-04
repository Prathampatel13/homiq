"""create payments table

Revision ID: aff4767f7b5e
Revises: 0810_fix_bookings_foreign_keys
Create Date: 2026-07-25 11:07:34.526587
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "aff4767f7b5e"
down_revision: Union[str, Sequence[str], None] = "0810_fix_bookings_foreign_keys"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if "payments" in tables:
        op.drop_table("payments")

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),

        sa.Column(
            "booking_id",
            sa.Integer(),
            sa.ForeignKey("bookings.id", ondelete="CASCADE"),
            nullable=False,
        ),

        sa.Column(
            "customer_id",
            sa.Integer(),
            sa.ForeignKey("customers.id", ondelete="CASCADE"),
            nullable=False,
        ),

        sa.Column(
            "amount",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "currency",
            sa.String(length=10),
            nullable=False,
            server_default="INR",
        ),

        sa.Column(
            "razorpay_order_id",
            sa.String(length=255),
            nullable=True,
            unique=True,
        ),

        sa.Column(
            "razorpay_payment_id",
            sa.String(length=255),
            nullable=True,
            unique=True,
        ),

        sa.Column(
            "razorpay_signature",
            sa.String(length=500),
            nullable=True,
        ),

        sa.Column(
            "payment_method",
            sa.Enum(
                "CARD",
                "UPI",
                "NETBANKING",
                "WALLET",
                "EMI",
                "UNKNOWN",
                name="paymentmethod",
                native_enum=False,
            ),
            nullable=False,
            server_default="UNKNOWN",
        ),

        sa.Column(
            "status",
            sa.Enum(
                "CREATED",
                "PAID",
                "FAILED",
                "REFUNDED",
                name="paymentstatus",
                native_enum=False,
            ),
            nullable=False,
            server_default="CREATED",
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_index(
        "ix_payments_id",
        "payments",
        ["id"],
    )

    op.create_index(
        "ix_payments_booking_id",
        "payments",
        ["booking_id"],
    )

    op.create_index(
        "ix_payments_customer_id",
        "payments",
        ["customer_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index("ix_payments_customer_id", table_name="payments")
    op.drop_index("ix_payments_booking_id", table_name="payments")
    op.drop_index("ix_payments_id", table_name="payments")

    op.drop_table("payments")