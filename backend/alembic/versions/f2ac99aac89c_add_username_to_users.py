"""add_username_to_users

Revision ID: f2ac99aac89c
Revises: 946c31cd1296
Create Date: 2026-08-27 14:54:40.785775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2ac99aac89c'
down_revision: Union[str, Sequence[str], None] = '946c31cd1296'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
