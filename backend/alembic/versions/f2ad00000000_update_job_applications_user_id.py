"""update job applications user id

Revision ID: f2ad00000000
Revises: f2ac99aac89c
Create Date: 2026-09-08 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2ad00000000'
down_revision: Union[str, Sequence[str], None] = 'f2ac99aac89c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename technician_id to user_id
    op.alter_column(
        'job_applications',
        'technician_id',
        new_column_name='user_id',
        existing_type=sa.Integer(),
        existing_nullable=False,
    )
    # Drop old foreign key constraint
    op.drop_constraint('job_applications_technician_id_fkey', 'job_applications', type_='foreignkey')
    # Add new foreign key constraint
    op.create_foreign_key('job_applications_user_id_fkey', 'job_applications', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    # Drop new foreign key constraint
    op.drop_constraint('job_applications_user_id_fkey', 'job_applications', type_='foreignkey')
    # Add old foreign key constraint
    op.create_foreign_key('job_applications_technician_id_fkey', 'job_applications', 'technicians', ['user_id'], ['id'])
    
    # Rename user_id back to technician_id
    op.alter_column(
        'job_applications',
        'user_id',
        new_column_name='technician_id',
        existing_type=sa.Integer(),
        existing_nullable=False,
    )
