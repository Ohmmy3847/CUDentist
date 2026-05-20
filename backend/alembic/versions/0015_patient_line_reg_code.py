"""add line_reg_code to patients

Revision ID: 0015
Revises: 0014
Create Date: 2026-05-16
"""
from alembic import op
import sqlalchemy as sa

revision = '0015'
down_revision = '0014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('patients', sa.Column('line_reg_code', sa.String(8), nullable=True, unique=True))


def downgrade() -> None:
    op.drop_column('patients', 'line_reg_code')
