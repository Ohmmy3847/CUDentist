"""add granular review flags to assessment_results

Revision ID: 0018
Revises: 0017
Create Date: 2026-05-18
"""

from alembic import op
import sqlalchemy as sa

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("assessment_results", sa.Column("needs_review_question", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("assessment_results", sa.Column("needs_review_custom", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("assessment_results", sa.Column("needs_review_conflict", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.alter_column("assessment_results", "needs_review_question", server_default=None)
    op.alter_column("assessment_results", "needs_review_custom", server_default=None)
    op.alter_column("assessment_results", "needs_review_conflict", server_default=None)


def downgrade() -> None:
    op.drop_column("assessment_results", "needs_review_conflict")
    op.drop_column("assessment_results", "needs_review_custom")
    op.drop_column("assessment_results", "needs_review_question")

