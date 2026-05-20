"""add email_otps table

Revision ID: 0021
Revises: 0020
Create Date: 2026-05-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0021'
down_revision: Union[str, None] = '0020'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'email_otps',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_token', sa.String(64), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(6), nullable=False),
        sa.Column('purpose', sa.String(32), nullable=False),
        sa.Column('payload', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_email_otps_session_token', 'email_otps', ['session_token'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_email_otps_session_token', table_name='email_otps')
    op.drop_table('email_otps')
