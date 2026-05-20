"""add line_sent to form_tokens

Revision ID: 0014
Revises: 0013
Create Date: 2026-05-16
"""
from alembic import op
import sqlalchemy as sa

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("form_tokens", sa.Column("line_sent", sa.Boolean(), nullable=False, server_default="false"))


def downgrade():
    op.drop_column("form_tokens", "line_sent")
