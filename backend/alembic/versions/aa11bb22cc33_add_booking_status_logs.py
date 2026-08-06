"""Add booking_status_logs audit table

Revision ID: aa11bb22cc33
Revises: 74cbbc2dbc75
Create Date: 2026-07-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "aa11bb22cc33"
down_revision: Union[str, Sequence[str], None] = "74cbbc2dbc75"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create booking_status_logs table for the booking lifecycle audit trail.
    op.create_table(
        "booking_status_logs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "booking_id",
            sa.Integer(),
            sa.ForeignKey("bookings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "old_status",
            sa.Enum(
                "PENDING",
                "ASSIGNED",
                "ACCEPTED",
                "ON_THE_WAY",
                "ARRIVED",
                "WAITING_QR",
                "QR_VERIFIED",
                "IN_PROGRESS",
                "COMPLETED",
                "WAITING_PAYMENT",
                "PAID",
                "REVIEW_PENDING",
                "CLOSED",
                "CANCELLED",
                "EXPIRED",
                "REJECTED",
                name="bookingstatus",
                native_enum=False,
            ),
            nullable=True,
        ),
        sa.Column(
            "new_status",
            sa.Enum(
                "PENDING",
                "ASSIGNED",
                "ACCEPTED",
                "ON_THE_WAY",
                "ARRIVED",
                "WAITING_QR",
                "QR_VERIFIED",
                "IN_PROGRESS",
                "COMPLETED",
                "WAITING_PAYMENT",
                "PAID",
                "REVIEW_PENDING",
                "CLOSED",
                "CANCELLED",
                "EXPIRED",
                "REJECTED",
                name="bookingstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("changed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_booking_status_logs_id",
        "booking_status_logs",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_booking_status_logs_booking_id",
        "booking_status_logs",
        ["booking_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_booking_status_logs_booking_id",
        table_name="booking_status_logs",
    )
    op.drop_index(
        "ix_booking_status_logs_id",
        table_name="booking_status_logs",
    )
    op.drop_table("booking_status_logs")
