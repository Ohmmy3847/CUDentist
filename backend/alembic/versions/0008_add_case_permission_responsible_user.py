"""add add_case permission and responsible_user_id to patients

Revision ID: 0008
Revises: 0007
Create Date: 2026-05-15
"""
from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade():
    # Add responsible_user_id to patients
    op.add_column("patients", sa.Column("responsible_user_id", sa.Integer, sa.ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True))

    # Grant add_case to all users who already have fill_assessment
    op.execute("""
        UPDATE users
        SET roles = (roles::jsonb || '["add_case"]'::jsonb)
        WHERE roles::jsonb @> '["fill_assessment"]'::jsonb
          AND NOT roles::jsonb @> '["add_case"]'::jsonb
    """)


def downgrade():
    op.drop_column("patients", "responsible_user_id")
    op.execute("""
        UPDATE users
        SET roles = (
            SELECT jsonb_agg(r)
            FROM jsonb_array_elements_text(roles::jsonb) AS r
            WHERE r != 'add_case'
        )
    """)
