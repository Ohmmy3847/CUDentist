"""add password_hash to form_tokens

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("form_tokens", sa.Column("password_hash", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("form_tokens", "password_hash")
