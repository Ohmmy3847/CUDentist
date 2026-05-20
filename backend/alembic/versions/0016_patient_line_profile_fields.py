"""add line profile fields to patients

Revision ID: 0016
Revises: 0015
Create Date: 2026-05-18
"""

from alembic import op
import sqlalchemy as sa

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("patients", sa.Column("line_display_name", sa.String(256), nullable=True))
    op.add_column("patients", sa.Column("line_picture_url", sa.String(1000), nullable=True))


def downgrade() -> None:
    op.drop_column("patients", "line_picture_url")
    op.drop_column("patients", "line_display_name")

