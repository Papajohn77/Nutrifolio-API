"""create tags & product_tag tables

Revision ID: 0d595861f6cc
Revises: d901609526e0
Create Date: 2022-06-16 08:53:15.055693

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d595861f6cc'
down_revision = 'd901609526e0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('tags',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('label')
    )

    op.create_table('product_tag',
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
        sa.PrimaryKeyConstraint('product_id', 'tag_id')
    )


def downgrade():
    op.drop_table('product_tag')
    op.drop_table('tags')
