"""migrate role values to permission-based system

Revision ID: 0007
Revises: 0006
Create Date: 2026-05-15
"""
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade():
    # nurse + admin → all four (must run first before more specific cases)
    op.execute("""
        UPDATE users
        SET roles = '["fill_assessment", "view_cases", "manage_users", "manage_docs"]'
        WHERE roles::jsonb @> '["nurse"]'::jsonb
          AND roles::jsonb @> '["admin"]'::jsonb
    """)
    # nurse only → [fill_assessment, view_cases]
    op.execute("""
        UPDATE users
        SET roles = '["fill_assessment", "view_cases"]'
        WHERE roles::jsonb @> '["nurse"]'::jsonb
          AND NOT roles::jsonb @> '["admin"]'::jsonb
          AND NOT roles::jsonb @> '["fill_assessment"]'::jsonb
    """)
    # admin only → [manage_users, manage_docs]
    op.execute("""
        UPDATE users
        SET roles = '["manage_users", "manage_docs"]'
        WHERE roles::jsonb @> '["admin"]'::jsonb
          AND NOT roles::jsonb @> '["nurse"]'::jsonb
          AND NOT roles::jsonb @> '["manage_users"]'::jsonb
    """)


def downgrade():
    op.execute("""
        UPDATE users
        SET roles = '["nurse"]'::jsonb
        WHERE roles @> '["fill_assessment"]'::jsonb
          AND NOT roles @> '["manage_users"]'::jsonb
    """)
    op.execute("""
        UPDATE users
        SET roles = '["admin"]'::jsonb
        WHERE roles @> '["manage_users"]'::jsonb
          AND NOT roles @> '["fill_assessment"]'::jsonb
    """)
    op.execute("""
        UPDATE users
        SET roles = '["nurse", "admin"]'::jsonb
        WHERE roles @> '["fill_assessment"]'::jsonb
          AND roles @> '["manage_users"]'::jsonb
    """)
