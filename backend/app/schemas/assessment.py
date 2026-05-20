from datetime import datetime
from typing import Any
from pydantic import BaseModel


class AssessmentCreate(BaseModel):
    patient_hn: str
    symptom_values: dict[str, Any] | None = None
    custom_symptoms: list[Any] | None = None
    additional_questions: str | None = None
    language: str = "th"
    basic_info: dict[str, Any] | None = None
    submitted_at: datetime | None = None


class AssessmentResultOut(BaseModel):
    result_id: int
    assessment_id: int
    overall_risk: str | None
    flow_results: dict | None
    clinical_summary: str | None
    qa_answer: dict | None
    qa_chunks: list | None = None
    needs_review: bool = False
    needs_review_question: bool = False
    needs_review_custom: bool = False
    needs_review_conflict: bool = False
    reviewed_by: int | None = None
    patient_notified_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AssessmentResultUpdate(BaseModel):
    clinical_summary: str | None = None
    qa_answer_text: str | None = None
    needs_review: bool | None = None
    # granular confirmations (set true when staff confirms that part is OK)
    confirm_question: bool | None = None
    confirm_custom: bool | None = None
    confirm_conflict: bool | None = None


class AssessmentOut(BaseModel):
    assessment_id: int
    patient_hn: str
    created_by: int | None
    submitted_at: datetime
    symptom_values: dict | None
    custom_symptoms: list | None
    additional_questions: str | None
    language: str
    result: AssessmentResultOut | None = None

    model_config = {"from_attributes": True}


class AssessmentListItem(BaseModel):
    assessment_id: int
    patient_hn: str
    submitted_at: datetime
    overall_risk: str | None = None
    language: str

    model_config = {"from_attributes": True}
