"""update job posts to creator_id

Revision ID: f2ae00000000
Revises: f2ad00000000
Create Date: 2026-09-08 15:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2ae00000000'
down_revision: Union[str, Sequence[str], None] = 'f2ad00000000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename company_id to creator_id
    op.alter_column(
        'job_posts',
        'company_id',
        new_column_name='creator_id',
        existing_type=sa.Integer(),
        existing_nullable=False,
    )
    # Drop old foreign key constraint
    op.drop_constraint('job_posts_company_id_fkey', 'job_posts', type_='foreignkey')
    # Add new foreign key constraint
    op.create_foreign_key('job_posts_creator_id_fkey', 'job_posts', 'users', ['creator_id'], ['id'])


def downgrade() -> None:
    # Drop new foreign key constraint
    op.drop_constraint('job_posts_creator_id_fkey', 'job_posts', type_='foreignkey')
    # Add old foreign key constraint
    op.create_foreign_key('job_posts_company_id_fkey', 'job_posts', 'companies', ['creator_id'], ['id'])
    
    # Rename creator_id back to company_id
    op.alter_column(
        'job_posts',
        'creator_id',
        new_column_name='company_id',
        existing_type=sa.Integer(),
        existing_nullable=False,
    )
