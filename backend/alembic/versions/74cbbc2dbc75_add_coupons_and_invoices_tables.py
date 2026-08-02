"""add_coupons_and_invoices_tables

Revision ID: 74cbbc2dbc75
Revises: aff4767f7b5e
Create Date: 2026-07-25 14:41:23.251890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '74cbbc2dbc75'
down_revision: Union[str, Sequence[str], None] = 'aff4767f7b5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create coupons table
    op.create_table('coupons',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('discount_type', sa.String(length=20), nullable=False),
    sa.Column('discount_value', sa.Float(), nullable=False),
    sa.Column('min_order_value', sa.Float(), nullable=True),
    sa.Column('max_discount', sa.Float(), nullable=True, comment='Maximum discount amount for percentage coupons'),
    sa.Column('usage_limit', sa.Integer(), nullable=True, comment='Total number of times this coupon can be used'),
    sa.Column('usage_count', sa.Integer(), nullable=False),
    sa.Column('per_user_limit', sa.Integer(), nullable=False, comment='Maximum times a single user can use this coupon'),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('valid_from', sa.Date(), nullable=False),
    sa.Column('valid_until', sa.Date(), nullable=False),
    sa.Column('applicable_services', sa.Text(), nullable=True, comment='JSON list of service IDs this coupon applies to (null = all)'),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coupons_code'), 'coupons', ['code'], unique=True)
    op.create_index(op.f('ix_coupons_id'), 'coupons', ['id'], unique=False)

    # Create coupon_usages table
    op.create_table('coupon_usages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('coupon_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=True),
    sa.Column('discount_amount', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['coupon_id'], ['coupons.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coupon_usages_coupon_id'), 'coupon_usages', ['coupon_id'], unique=False)
    op.create_index(op.f('ix_coupon_usages_id'), 'coupon_usages', ['id'], unique=False)
    op.create_index(op.f('ix_coupon_usages_user_id'), 'coupon_usages', ['user_id'], unique=False)

    # Create invoices table
    op.create_table('invoices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('invoice_number', sa.String(length=100), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('payment_id', sa.Integer(), nullable=True),
    sa.Column('subtotal', sa.Float(), nullable=False, comment='Total before tax and discount'),
    sa.Column('discount_amount', sa.Float(), nullable=False),
    sa.Column('coupon_code', sa.String(length=50), nullable=True),
    sa.Column('tax_percentage', sa.Float(), nullable=False),
    sa.Column('tax_amount', sa.Float(), nullable=False),
    sa.Column('total_amount', sa.Float(), nullable=False, comment='Final amount after tax and discount'),
    sa.Column('amount_paid', sa.Float(), nullable=False),
    sa.Column('amount_due', sa.Float(), nullable=False),
    sa.Column('status', sa.Enum('DRAFT', 'ISSUED', 'PAID', 'PARTIALLY_PAID', 'OVERDUE', 'CANCELLED', 'REFUNDED', name='invoicestatus', native_enum=False), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('issued_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('due_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoices_booking_id'), 'invoices', ['booking_id'], unique=False)
    op.create_index(op.f('ix_invoices_customer_id'), 'invoices', ['customer_id'], unique=False)
    op.create_index(op.f('ix_invoices_id'), 'invoices', ['id'], unique=False)
    op.create_index(op.f('ix_invoices_invoice_number'), 'invoices', ['invoice_number'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_invoices_invoice_number'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_id'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_customer_id'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_booking_id'), table_name='invoices')
    op.drop_table('invoices')
    op.drop_index(op.f('ix_coupon_usages_user_id'), table_name='coupon_usages')
    op.drop_index(op.f('ix_coupon_usages_id'), table_name='coupon_usages')
    op.drop_index(op.f('ix_coupon_usages_coupon_id'), table_name='coupon_usages')
    op.drop_table('coupon_usages')
    op.drop_index(op.f('ix_coupons_id'), table_name='coupons')
    op.drop_index(op.f('ix_coupons_code'), table_name='coupons')
    op.drop_table('coupons')
