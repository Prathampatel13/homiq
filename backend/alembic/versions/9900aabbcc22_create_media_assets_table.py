"""create_media_assets_table

Revision ID: 9900aabbcc22
Revises: 8899aabbcc11
Create Date: 2026-08-22 00:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9900aabbcc22'
down_revision: Union[str, Sequence[str], None] = '8899aabbcc11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - create media_assets table and add avatar_url to users."""
    op.create_table(
        'media_assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('owner_type', sa.String(length=50), nullable=False),
        sa.Column('asset_type', sa.String(length=50), nullable=False),
        sa.Column('cloudinary_asset_id', sa.String(length=100), nullable=True),
        sa.Column('cloudinary_public_id', sa.String(length=255), nullable=False),
        sa.Column('secure_url', sa.String(length=500), nullable=False),
        sa.Column('resource_type', sa.String(length=30), nullable=False, server_default='image'),
        sa.Column('format', sa.String(length=20), nullable=False, server_default=''),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cloudinary_public_id')
    )
    op.create_index(op.f('ix_media_assets_id'), 'media_assets', ['id'], unique=False)
    op.create_index(op.f('ix_media_assets_owner_id'), 'media_assets', ['owner_id'], unique=False)
    op.create_index(op.f('ix_media_assets_owner_type'), 'media_assets', ['owner_type'], unique=False)
    op.create_index(op.f('ix_media_assets_asset_type'), 'media_assets', ['asset_type'], unique=False)
    op.create_index(op.f('ix_media_assets_cloudinary_public_id'), 'media_assets', ['cloudinary_public_id'], unique=True)

    # Safe addition of avatar_url to users table if not existing
    try:
        op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=True))
    except Exception:
        pass


def downgrade() -> None:
    """Downgrade schema - drop media_assets table and avatar_url."""
    try:
        op.drop_column('users', 'avatar_url')
    except Exception:
        pass

    op.drop_index(op.f('ix_media_assets_cloudinary_public_id'), table_name='media_assets')
    op.drop_index(op.f('ix_media_assets_asset_type'), table_name='media_assets')
    op.drop_index(op.f('ix_media_assets_owner_type'), table_name='media_assets')
    op.drop_index(op.f('ix_media_assets_owner_id'), table_name='media_assets')
    op.drop_index(op.f('ix_media_assets_id'), table_name='media_assets')
    op.drop_table('media_assets')
