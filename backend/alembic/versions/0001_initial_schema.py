"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column("full_name", sa.String(length=128), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "patients",
        sa.Column("hn", sa.String(length=32), nullable=False),
        sa.Column("first_name", sa.String(length=64), nullable=False),
        sa.Column("last_name", sa.String(length=64), nullable=False),
        sa.Column("gender", sa.String(length=16), nullable=True),
        sa.Column("date_of_birth", sa.String(length=16), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("procedures", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("hn"),
    )

    op.create_table(
        "assessments",
        sa.Column("assessment_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("patient_hn", sa.String(length=32), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("symptom_values", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("custom_symptoms", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("additional_questions", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=4), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.user_id"]),
        sa.ForeignKeyConstraint(["patient_hn"], ["patients.hn"]),
        sa.PrimaryKeyConstraint("assessment_id"),
    )
    op.create_index("ix_assessments_patient_hn", "assessments", ["patient_hn"])

    op.create_table(
        "assessment_results",
        sa.Column("result_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("assessment_id", sa.Integer(), nullable=False),
        sa.Column("overall_risk", sa.String(length=32), nullable=True),
        sa.Column("flow_results", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("clinical_summary", sa.Text(), nullable=True),
        sa.Column("qa_answer", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.assessment_id"]),
        sa.PrimaryKeyConstraint("result_id"),
        sa.UniqueConstraint("assessment_id"),
    )

    op.create_table(
        "documents",
        sa.Column("document_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("filename", sa.String(length=256), nullable=False),
        sa.Column("file_type", sa.String(length=8), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("file_path", sa.String(length=512), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.Column("rag_status", sa.String(length=16), nullable=False),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("document_id"),
    )

    op.create_table(
        "symptoms",
        sa.Column("symptom_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symptom_name", sa.String(length=128), nullable=False),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("management_guidance", sa.Text(), nullable=True),
        sa.Column("managed_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["managed_by"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("symptom_id"),
    )


def downgrade() -> None:
    op.drop_table("symptoms")
    op.drop_table("documents")
    op.drop_table("assessment_results")
    op.drop_table("assessments")
    op.drop_table("patients")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
