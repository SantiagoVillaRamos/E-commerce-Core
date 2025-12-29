"""Initial schema with products, orders, and order_items tables

Revision ID: 001_initial
Revises: 
Create Date: 2025-12-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create products table
    op.create_table(
        'products',
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sku', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=False, server_default=''),
        sa.Column('price_amount', sa.Float(), nullable=False),
        sa.Column('price_currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('stock_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('product_id')
    )
    op.create_index('ix_products_sku', 'products', ['sku'], unique=True)
    
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', sa.String(length=100), nullable=False),
        sa.Column('customer_name', sa.String(length=255), nullable=False),
        sa.Column('customer_email', sa.String(length=255), nullable=False),
        sa.Column('customer_phone', sa.String(length=50), nullable=False),
        sa.Column('shipping_street', sa.String(length=500), nullable=False),
        sa.Column('shipping_city', sa.String(length=100), nullable=False),
        sa.Column('shipping_state', sa.String(length=100), nullable=False),
        sa.Column('shipping_postal_code', sa.String(length=20), nullable=False),
        sa.Column('shipping_country', sa.String(length=100), nullable=False, server_default='Colombia'),
        sa.Column('status', sa.Enum('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', name='orderstatusenum'), nullable=False, server_default='pending'),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('confirmed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('order_id')
    )
    op.create_index('ix_orders_customer_id', 'orders', ['customer_id'])
    
    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('item_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('item_id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ondelete='CASCADE')
    )


def downgrade() -> None:
    op.drop_table('order_items')
    op.drop_index('ix_orders_customer_id', table_name='orders')
    op.drop_table('orders')
    op.drop_index('ix_products_sku', table_name='products')
    op.drop_table('products')
    op.execute('DROP TYPE orderstatusenum')
