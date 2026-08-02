"""Fix bookings foreign keys — point to correct tables

Revision ID: 0810_fix_bookings_foreign_keys
Revises: 0809cdbcf61b
Create Date: 2026-07-24 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0810_fix_bookings_foreign_keys"
down_revision: Union[str, Sequence[str], None] = "0809cdbcf61b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix foreign keys on bookings table.

    Migration 0809cdbcf61b incorrectly set:
      - bookings.customer_id  → users.id
      - bookings.technician_id → users.id

    This migration corrects them to:
      - bookings.customer_id   → customers.id (ON DELETE CASCADE)
      - bookings.technician_id → technicians.id (ON DELETE SET NULL)
    """

    # Drop the wrong foreign keys created by 0809cdbcf61b.
    # PostgreSQL names them automatically; we use the constraint names
    # that were auto-generated. Adjust names if using a different dialect.
    op.drop_constraint(
        "bookings_customer_id_fkey",
        "bookings",
        type_="foreignkey",
    )
    op.drop_constraint(
        "bookings_technician_id_fkey",
        "bookings",
        type_="foreignkey",
    )

    # Recreate with the correct target tables
    op.create_foreign_key(
        "bookings_customer_id_fkey",
        "bookings",
        "customers",           # ← correct: customers, not users
        ["customer_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "bookings_technician_id_fkey",
        "bookings",
        "technicians",         # ← correct: technicians, not users
        ["technician_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Revert to the (wrong) foreign keys pointing to users.id."""

    op.drop_constraint(
        "bookings_customer_id_fkey",
        "bookings",
        type_="foreignkey",
    )
    op.drop_constraint(
        "bookings_technician_id_fkey",
        "bookings",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "bookings_customer_id_fkey",
        "bookings",
        "users",
        ["customer_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "bookings_technician_id_fkey",
        "bookings",
        "users",
        ["technician_id"],
        ["id"],
        ondelete="SET NULL",
    )

