"""create products table

Revision ID: 95d12e667dcd
Revises: 5151836306a3
Create Date: 2022-06-15 19:11:55.453511

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '95d12e667dcd'
down_revision = '5151836306a3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('products',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('image_url', sa.String(), nullable=False),
        sa.Column('calories', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(), nullable=False),
        sa.Column('store_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('products')
