"""add qa_chunks to assessment_results

Revision ID: 0011
Revises: 0010
Create Date: 2026-05-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("assessment_results", sa.Column("qa_chunks", JSONB, nullable=True))


def downgrade():
    op.drop_column("assessment_results", "qa_chunks")
