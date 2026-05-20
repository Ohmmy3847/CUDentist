"""replace role string with roles jsonb array

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-15
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("roles", sa.JSON, nullable=True))
    op.execute("UPDATE users SET roles = json_build_array(role)")
    op.alter_column("users", "roles", nullable=False)
    op.drop_column("users", "role")


def downgrade():
    op.add_column("users", sa.Column("role", sa.String(16), nullable=True))
    op.execute("UPDATE users SET role = roles->>0")
    op.alter_column("users", "role", nullable=False)
    op.drop_column("users", "roles")
