"""create orders tables

Revision ID: 005
Revises: 004
Create Date: 2024-02-10
"""
from alembic import op
import sqlalchemy as sa

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Criar enum para status
    op.execute("CREATE TYPE orderstatus AS ENUM ('pending', 'paid', 'cancelled', 'delivered')")
    
    # Criar tabela orders
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('total', sa.Float(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'paid', 'cancelled', 'delivered', name='orderstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar tabela order_items
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('order_items')
    op.drop_table('orders')
    op.execute('DROP TYPE orderstatus')
