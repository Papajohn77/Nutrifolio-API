"""create users table

Revision ID: e12e23310314
Revises: 
Create Date: 2022-06-15 11:03:49.459447

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = 'e12e23310314'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('first_name', sa.String, nullable=False),
        sa.Column('last_name', sa.String, nullable=False),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('password', sa.String, nullable=False),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            server_default=func.now(),
            nullable=False
        )
    )


def downgrade():
    op.drop_table('users')
