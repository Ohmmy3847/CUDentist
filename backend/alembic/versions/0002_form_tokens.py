"""add form_tokens table

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "form_tokens",
        sa.Column("token", sa.String(length=36), nullable=False),
        sa.Column("patient_hn", sa.String(length=32), nullable=False),
        sa.Column("schedule_date", sa.String(length=32), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["patient_hn"], ["patients.hn"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("token"),
    )
    op.create_index("ix_form_tokens_patient_hn", "form_tokens", ["patient_hn"])


def downgrade() -> None:
    op.drop_index("ix_form_tokens_patient_hn", table_name="form_tokens")
    op.drop_table("form_tokens")
