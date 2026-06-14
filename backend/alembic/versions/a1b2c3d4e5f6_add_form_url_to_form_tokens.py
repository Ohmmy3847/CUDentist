"""add form_url to form_tokens

Revision ID: a1b2c3d4e5f6
Revises: 27ddd042ac53
Create Date: 2026-06-14
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '27ddd042ac53'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('form_tokens', sa.Column('form_url', sa.String(512), nullable=True))


def downgrade() -> None:
    op.drop_column('form_tokens', 'form_url')
