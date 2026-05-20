"""add needs_review and reviewed_by to assessment_results

Revision ID: 0010
Revises: 0009
Create Date: 2026-05-15
"""
from alembic import op
import sqlalchemy as sa

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("assessment_results", sa.Column("needs_review", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("assessment_results", sa.Column("reviewed_by", sa.Integer(), sa.ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True))

    # Mark existing results as needing review if their assessment has custom_symptoms
    op.execute("""
        UPDATE assessment_results ar
        SET needs_review = true
        FROM assessments a
        WHERE ar.assessment_id = a.assessment_id
          AND a.custom_symptoms IS NOT NULL
          AND jsonb_array_length(a.custom_symptoms::jsonb) > 0
    """)


def downgrade():
    op.drop_column("assessment_results", "reviewed_by")
    op.drop_column("assessment_results", "needs_review")
