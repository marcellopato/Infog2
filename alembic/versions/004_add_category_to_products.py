"""add category to products

Revision ID: 004
Revises: 003
Create Date: 2024-02-10
"""
from alembic import op
import sqlalchemy as sa

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Adicionar coluna category_id
    op.add_column('products', 
        sa.Column('category_id', sa.Integer(), nullable=True)
    )
    # Adicionar foreign key
    op.create_foreign_key(
        'fk_product_category',
        'products', 'categories',
        ['category_id'], ['id']
    )

def downgrade() -> None:
    op.drop_constraint('fk_product_category', 'products', type_='foreignkey')
    op.drop_column('products', 'category_id')
