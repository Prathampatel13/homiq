"""merge heads

Revision ID: f2af00000000
Revises: f2ae00000000, fcc910155e51
Create Date: 2026-09-08 19:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2af00000000'
down_revision: Union[str, Sequence[str], None] = ('f2ae00000000', 'fcc910155e51')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
