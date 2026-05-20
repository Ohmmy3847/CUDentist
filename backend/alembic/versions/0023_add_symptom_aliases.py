"""add symptom aliases

Revision ID: 0023
Revises: 0022
"""
from typing import Union
from alembic import op
import sqlalchemy as sa

revision: str = '0023'
down_revision: Union[str, None] = '0022'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('symptoms', sa.Column('aliases', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('symptoms', 'aliases')
