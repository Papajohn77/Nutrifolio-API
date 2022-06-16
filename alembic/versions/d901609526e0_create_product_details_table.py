"""create product_details table

Revision ID: d901609526e0
Revises: 95d12e667dcd
Create Date: 2022-06-15 19:48:39.574710

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd901609526e0'
down_revision = '95d12e667dcd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('product_details',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('weight', sa.Integer(), nullable=False),
        sa.Column('protein', sa.Integer(), nullable=False),
        sa.Column('carbohydrates', sa.Integer(), nullable=False),
        sa.Column('fiber', sa.Float(), nullable=True),
        sa.Column('sugars', sa.Float(), nullable=True),
        sa.Column('fat', sa.Integer(), nullable=False),
        sa.Column('saturated_fat', sa.Float(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id')
    )

    op.add_column('products', sa.Column('category', sa.String(), nullable=False))


def downgrade():
    op.drop_column('products', 'category')
    op.drop_table('product_details')
