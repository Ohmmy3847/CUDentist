"""set ON DELETE SET NULL on user FK references

Revision ID: 0006
Revises: 0005
Create Date: 2026-05-15
"""
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    # assessments.created_by
    op.drop_constraint("assessments_created_by_fkey", "assessments", type_="foreignkey")
    op.create_foreign_key(
        "assessments_created_by_fkey", "assessments", "users",
        ["created_by"], ["user_id"], ondelete="SET NULL"
    )

    # documents.uploaded_by
    op.drop_constraint("documents_uploaded_by_fkey", "documents", type_="foreignkey")
    op.create_foreign_key(
        "documents_uploaded_by_fkey", "documents", "users",
        ["uploaded_by"], ["user_id"], ondelete="SET NULL"
    )

    # symptoms.managed_by
    op.drop_constraint("symptoms_managed_by_fkey", "symptoms", type_="foreignkey")
    op.create_foreign_key(
        "symptoms_managed_by_fkey", "symptoms", "users",
        ["managed_by"], ["user_id"], ondelete="SET NULL"
    )


def downgrade():
    op.drop_constraint("assessments_created_by_fkey", "assessments", type_="foreignkey")
    op.create_foreign_key(
        "assessments_created_by_fkey", "assessments", "users",
        ["created_by"], ["user_id"]
    )

    op.drop_constraint("documents_uploaded_by_fkey", "documents", type_="foreignkey")
    op.create_foreign_key(
        "documents_uploaded_by_fkey", "documents", "users",
        ["uploaded_by"], ["user_id"]
    )

    op.drop_constraint("symptoms_managed_by_fkey", "symptoms", type_="foreignkey")
    op.create_foreign_key(
        "symptoms_managed_by_fkey", "symptoms", "users",
        ["managed_by"], ["user_id"]
    )
