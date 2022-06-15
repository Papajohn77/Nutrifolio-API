"""create stores table

Revision ID: 5151836306a3
Revises: e12e23310314
Create Date: 2022-06-15 16:39:29.523849

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5151836306a3'
down_revision = 'e12e23310314'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('stores',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('logo_url', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lng', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )


def downgrade():
    op.drop_table('stores')
