"""
Pydantic Models for API Request/Response
"""
from pydantic import BaseModel
from typing import Dict, Optional, Any


class PatientData(BaseModel):
    """Patient data for classification"""
    data: Dict[str, Any]
    flow_name: Optional[str] = None  # ถ้าไม่ระบุจะรันทุก flow


class RiskResponse(BaseModel):
    """Response model for single risk classification"""
    risk_level: str
    recommendation: str
    reason: str


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
