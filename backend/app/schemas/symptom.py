from pydantic import BaseModel


class SymptomCreate(BaseModel):
    symptom_name: str
    risk_level: str = "low"
    recommendation: str | None = None
    management_guidance: str | None = None
    aliases: list[str] | None = None


class SymptomUpdate(BaseModel):
    symptom_name: str | None = None
    risk_level: str | None = None
    recommendation: str | None = None
    management_guidance: str | None = None
    aliases: list[str] | None = None


class SymptomOut(BaseModel):
    symptom_id: int
    symptom_name: str
    risk_level: str
    recommendation: str | None
    management_guidance: str | None
    aliases: list[str] | None = None
    managed_by: int | None

    model_config = {"from_attributes": True}
