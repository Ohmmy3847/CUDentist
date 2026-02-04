"""
Pydantic Models for API Request/Response
"""
from pydantic import BaseModel
from typing import Dict, Optional, Any


class BasicInfo(BaseModel):
    """Basic patient information"""
    # Personal Information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    birth_year: Optional[int] = None
    
    # Basic Medical Info
    age: Optional[int] = None
    gender: Optional[str] = None
    hn: Optional[str] = None
    procedures: Optional[list] = None
    lefort_sub_options: Optional[list] = None
    bssro_sub_options: Optional[list] = None
    surgery_date: Optional[str] = None
    discharge_date: Optional[str] = None
    note: Optional[str] = None
    
    # Special Procedures
    has_imf: Optional[str] = None
    imf_type: Optional[str] = None
    imf_loops: Optional[int] = None
    special_icbg: Optional[str] = None
    special_icbg_description: Optional[str] = None
    special_ng_tube: Optional[str] = None
    special_ng_tube_description: Optional[str] = None


class PatientData(BaseModel):
    """Patient data for classification"""
    basic_info: BasicInfo
    assessment_data: Dict[str, Any]
    language: Optional[str] = 'th'
   


class RiskResponse(BaseModel):
    """Response model for single risk classification"""
    risk_level: str
    recommendation: str = None
    reason: str = None


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
