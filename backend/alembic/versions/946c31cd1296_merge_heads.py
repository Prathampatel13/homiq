"""merge heads

Revision ID: 946c31cd1296
Revises: 9900aabbcc22, aa11bb22cc33
Create Date: 2026-08-25 16:26:18.113935

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '946c31cd1296'
down_revision: Union[str, Sequence[str], None] = ('9900aabbcc22', 'aa11bb22cc33')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
