"""add is_superuser to users

Revision ID: 0020
Revises: 493e6d316f5b
Create Date: 2026-05-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0020'
down_revision: Union[str, None] = '493e6d316f5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'))
    # promote the earliest created user (initial admin) to superuser
    op.execute("UPDATE users SET is_superuser = true WHERE user_id = (SELECT MIN(user_id) FROM users)")


def downgrade() -> None:
    op.drop_column('users', 'is_superuser')
