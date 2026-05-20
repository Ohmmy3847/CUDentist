"""add patient_notified_at to assessment_results

Revision ID: 0017
Revises: 0016
Create Date: 2026-05-18
"""

from alembic import op
import sqlalchemy as sa

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("assessment_results", sa.Column("patient_notified_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("assessment_results", "patient_notified_at")

