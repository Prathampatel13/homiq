"""restore username

Revision ID: f2b000000000
Revises: f2af00000000
Create Date: 2026-09-08 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2b000000000'
down_revision: Union[str, Sequence[str], None] = 'f2af00000000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_cols = [c['name'] for c in inspector.get_columns('users')]
    
    if 'username' not in user_cols:
        op.add_column('users', sa.Column('username', sa.String(length=255), nullable=True))
        op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_indices = [idx['name'] for idx in inspector.get_indexes('users')]
    user_cols = [c['name'] for c in inspector.get_columns('users')]

    if 'ix_users_username' in user_indices:
        op.drop_index(op.f('ix_users_username'), table_name='users')
    if 'username' in user_cols:
        op.drop_column('users', 'username')
