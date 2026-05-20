from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Assessment(Base):
    __tablename__ = "assessments"

    assessment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_hn: Mapped[str] = mapped_column(String(32), ForeignKey("patients.hn"), nullable=False, index=True)
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"))
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    symptom_values: Mapped[dict | None] = mapped_column(JSONB)
    custom_symptoms: Mapped[list | None] = mapped_column(JSONB)
    additional_questions: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(4), default="th")

    patient: Mapped["Patient"] = relationship("Patient", back_populates="assessments")  # noqa: F821
    creator: Mapped["User"] = relationship("User", back_populates="assessments")  # noqa: F821
    result: Mapped["AssessmentResult | None"] = relationship("AssessmentResult", back_populates="assessment", uselist=False, lazy="select", cascade="all, delete-orphan")


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    result_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(Integer, ForeignKey("assessments.assessment_id"), nullable=False, unique=True)
    overall_risk: Mapped[str | None] = mapped_column(String(32))
    flow_results: Mapped[dict | None] = mapped_column(JSONB)
    clinical_summary: Mapped[str | None] = mapped_column(Text)
    qa_answer: Mapped[dict | None] = mapped_column(JSONB)
    qa_chunks: Mapped[list | None] = mapped_column(JSONB)
    needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    needs_review_question: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    needs_review_custom: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    needs_review_conflict: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reviewed_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    patient_notified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="result")
