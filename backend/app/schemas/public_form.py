from datetime import datetime
from typing import Any
from pydantic import BaseModel


class FormTokenOut(BaseModel):
    token: str
    url: str
    password: str
    expires_at: datetime

    model_config = {"from_attributes": True}


class PublicPatientInfo(BaseModel):
    first_name: str
    last_name: str
    gender: str | None = None
    date_of_birth: str | None = None
    phone: str | None = None
    procedures: list | None = None
    schedule_date: str | None = None


class PublicAssessmentSubmit(BaseModel):
    password: str
    basic_info: dict[str, Any] | None = None
    symptom_values: dict[str, Any] | None = None
    custom_symptoms: list[Any] | None = None
    additional_questions: str | None = None
    language: str = "th"
    submitted_at: datetime | None = None
