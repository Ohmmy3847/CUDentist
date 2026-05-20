"""rename fill_assessment -> send_assessment, add edit_case permission

Revision ID: 0009
Revises: 0008
Create Date: 2026-05-15
"""
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade():
    # Rename fill_assessment -> send_assessment
    op.execute("""
        UPDATE users
        SET roles = (
            SELECT jsonb_agg(
                CASE WHEN r = 'fill_assessment' THEN 'send_assessment' ELSE r END
            )
            FROM jsonb_array_elements_text(roles::jsonb) AS r
        )
        WHERE roles::jsonb @> '["fill_assessment"]'::jsonb
    """)

    # Grant edit_case to all users who already have add_case
    op.execute("""
        UPDATE users
        SET roles = (roles::jsonb || '["edit_case"]'::jsonb)
        WHERE roles::jsonb @> '["add_case"]'::jsonb
          AND NOT roles::jsonb @> '["edit_case"]'::jsonb
    """)


def downgrade():
    # Rename send_assessment -> fill_assessment
    op.execute("""
        UPDATE users
        SET roles = (
            SELECT jsonb_agg(
                CASE WHEN r = 'send_assessment' THEN 'fill_assessment' ELSE r END
            )
            FROM jsonb_array_elements_text(roles::jsonb) AS r
        )
        WHERE roles::jsonb @> '["send_assessment"]'::jsonb
    """)

    # Remove edit_case
    op.execute("""
        UPDATE users
        SET roles = (
            SELECT jsonb_agg(r)
            FROM jsonb_array_elements_text(roles::jsonb) AS r
            WHERE r != 'edit_case'
        )
    """)
