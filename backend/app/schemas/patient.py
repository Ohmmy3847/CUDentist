from datetime import datetime
from typing import Any
from pydantic import BaseModel


class PatientCreate(BaseModel):
    hn: str
    first_name: str
    last_name: str
    gender: str | None = None
    date_of_birth: str | None = None
    phone: str | None = None
    procedures: list[Any] | None = None
    follow_up_date: datetime | None = None
    follow_up_schedules: list[str] | None = None
    responsible_person: str | None = None
    responsible_user_id: int | None = None
    status: str = "active"
    extra_info: dict[str, Any] | None = None


class PatientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    gender: str | None = None
    date_of_birth: str | None = None
    phone: str | None = None
    procedures: list[Any] | None = None
    follow_up_date: datetime | None = None
    follow_up_schedules: list[str] | None = None
    responsible_person: str | None = None
    responsible_user_id: int | None = None
    status: str | None = None
    extra_info: dict[str, Any] | None = None


class PatientOut(BaseModel):
    hn: str
    first_name: str
    last_name: str
    gender: str | None
    date_of_birth: str | None
    phone: str | None
    procedures: list[Any] | None
    follow_up_date: datetime | None
    follow_up_schedules: list[str] | None
    responsible_person: str | None
    responsible_user_id: int | None
    responsible_nurse_name: str | None = None
    status: str
    extra_info: dict[str, Any] | None = None
    line_user_id: str | None = None
    line_reg_code: str | None = None
    line_display_name: str | None = None
    line_picture_url: str | None = None

    model_config = {"from_attributes": True}
