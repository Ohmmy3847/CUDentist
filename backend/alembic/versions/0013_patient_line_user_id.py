"""add line_user_id to patients

Revision ID: 0013
Revises: 0012
Create Date: 2026-05-16
"""
from alembic import op
import sqlalchemy as sa

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("patients", sa.Column("line_user_id", sa.String(64), nullable=True))
    op.create_index("ix_patients_line_user_id", "patients", ["line_user_id"], unique=True)


def downgrade():
    op.drop_index("ix_patients_line_user_id", table_name="patients")
    op.drop_column("patients", "line_user_id")
