"""unique constraint on form_tokens (patient_hn, schedule_date)

Revision ID: 0019
Revises: 0018
Create Date: 2026-05-18
"""
from alembic import op

revision = '0019'
down_revision = '0018'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        'uq_form_tokens_patient_schedule',
        'form_tokens',
        ['patient_hn', 'schedule_date'],
    )


def downgrade() -> None:
    op.drop_constraint('uq_form_tokens_patient_schedule', 'form_tokens')
