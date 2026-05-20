"""add extra_info to patients

Revision ID: 0012
Revises: 0011
Create Date: 2026-05-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = '0012'
down_revision = '0011'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('patients', sa.Column('extra_info', JSONB, nullable=True))


def downgrade():
    op.drop_column('patients', 'extra_info')
