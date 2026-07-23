"""Add missing fields to services table

Revision ID: 6b1f4f9a2e31
Revises: 55bf0050f96f
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6b1f4f9a2e31"
down_revision: Union[str, Sequence[str], None] = "55bf0050f96f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # duration_minutes
    op.add_column(
        "services",
        sa.Column(
            "duration_minutes",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    # image_url
    op.add_column(
        "services",
        sa.Column(
            "image_url",
            sa.String(length=500),
            nullable=True,
        ),
    )

    # is_active
    op.add_column(
        "services",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )

    # updated_at
    op.add_column(
        "services",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("services", "updated_at")
    op.drop_column("services", "is_active")
    op.drop_column("services", "image_url")
    op.drop_column("services", "duration_minutes")