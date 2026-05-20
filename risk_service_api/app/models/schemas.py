"""
Pydantic Models for API Request/Response
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class BasicInfo(BaseModel):
    """Basic patient information"""
    # Personal Information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[str] = None
    
    # Basic Medical Info
    gender: Optional[str] = None
    hn: Optional[str] = None
    procedures: Optional[list] = None
    lefort_sub_options: Optional[list] = None
    bssro_sub_options: Optional[list] = None
    surgery_date: Optional[str] = None
    discharge_date: Optional[str] = None
    note: Optional[str] = None
    
    # Special Procedures
    imf_wire: Optional[bool] = None
    imf_wire_loops: Optional[int] = None
    imf_elastic: Optional[bool] = None
    imf_elastic_loops: Optional[int] = None
    special_icbg: Optional[bool] = None
    special_icbg_description: Optional[str] = None
    special_ng_tube: Optional[bool] = None
    special_ng_tube_description: Optional[str] = None


class PatientData(BaseModel):
    """Patient data for classification"""
    basic_info: BasicInfo
    assessment_data: Dict[str, Any]
    language: Optional[str] = 'th'
    patient_question: Optional[str] = None

class RiskResponse(BaseModel):
    """Response model for single risk classification"""
    risk_level: str
    recommendation: Optional[str] = None
    reason: Optional[str] = None


class AllFlowsResult(BaseModel):
    """Response model for all flows classification"""
    results: Dict[str, RiskResponse]
    errors: Optional[Dict[str, str]] = None




class LogData(BaseModel):
    """Model for logging form submissions with AI results"""
    form_data: Dict[str, Any]
    results: Dict[str, Any]
    session_id: Optional[str] = None


class RawInputData(BaseModel):
    """Model for logging raw form input without AI results"""
    # Allow any fields from patient form
    class Config:
        extra = 'allow'  # Accept any additional fields


# ------------------------------------------------------------
# Risk Assessment Models (ย้ายมาจาก risk_service.py)
# ------------------------------------------------------------

class RiskSummaryContent(BaseModel):
    """Pydantic model for LLM risk summary output (due-to clause only)"""
    risk_summary: str = Field(description="Short phrase summarizing risk reasons (clause after due to / เนื่องจาก)")


class OutputRiskClassification(BaseModel):
    risk_level: str = Field(description="ระดับความเสี่ยงของผู้ป่วย [ความเสี่ยงต่ำ, ความเสี่ยงกลาง, ความเสี่ยงสูง]")
    recommendation: str = Field(description="คำแนะนำการดูแลตนเองสำหรับผู้ป่วย เขียนเป็นภาษาไทย ต้องบอกชัดว่าควรทำอะไร")
    reason: str = Field(description="เหตุผลที่ประเมินระดับความเสี่ยงนี้ เขียนเป็นภาษาไทย")


class RiskSummaryOutput(BaseModel):
    """Output model สำหรับ summarize_all_risks"""
    overall_risk: str = Field(description="ระดับความเสี่ยงโดยรวม")
    summary: str = Field(description="สรุปผลการประเมินสำหรับผู้ป่วย")


class PatientQuestionAnswer(BaseModel):
    """Output model สำหรับ answer_patient_questions"""
    answer: str = Field(description="คำตอบสำหรับผู้ป่วย")
    urgency_level: str = Field(description="ระดับความเร่งด่วน: ปกติ, ควรติดตาม, เร่งด่วน")
    should_contact_doctor: bool = Field(description="ควรติดต่อแพทย์หรือไม่")
    related_risks: List[str] = Field(default_factory=list, description="ความเสี่ยงที่เกี่ยวข้อง")