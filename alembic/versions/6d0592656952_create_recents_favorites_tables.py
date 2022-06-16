"""create recents & favorites tables

Revision ID: 6d0592656952
Revises: 0d595861f6cc
Create Date: 2022-06-16 09:57:39.923359

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d0592656952'
down_revision = '0d595861f6cc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('favorites',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'product_id')
    )
    op.create_table('recents',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'product_id')
    )


def downgrade():
    op.drop_table('recents')
    op.drop_table('favorites')
