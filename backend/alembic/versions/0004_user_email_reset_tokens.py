"""add user email and password_reset_tokens table

Revision ID: 0004
Revises: 1f5f05abae1b
Create Date: 2026-05-15
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "1f5f05abae1b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("email", sa.String(256), nullable=True))

    op.create_table(
        "password_reset_tokens",
        sa.Column("token", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.user_id"), nullable=False, index=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("password_reset_tokens")
    op.drop_column("users", "email")
