"""
Logging Router - Form Submission Logging Endpoints
"""
from fastapi import APIRouter, HTTPException
import logging
from datetime import datetime

from app.models.schemas import LogData, RawInputData
from app.services.log_service import append_raw_input, append_with_result
from app.services.risk_service import FORM_COLUMNS

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/log",
    tags=["logging"]
)


@router.post("/submission")
async def log_form_submission(log_data: LogData):
    """
    Log form submission to Google Sheets
    
    Example request:
    {
        "form_data": {"age": 25, "gender": "หญิง", ...},
        "results": {"อาการปวด": {"risk_level": "ต่ำ", ...}},
        "session_id": "user_123"
    }
    """
    try:
        timestamp = datetime.now().isoformat()
        
        # Log to Google Sheets
        append_with_result(log_data.form_data, log_data.results, FORM_COLUMNS)
        
        logger.info(f"Successfully logged form submission for session: {log_data.session_id}")
        
        return {
            "status": "success",
            "timestamp": timestamp,
            "session_id": log_data.session_id
        }
        
    except Exception as e:
        logger.error(f"Failed to log submission: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to log submission: {str(e)}"
        )


@router.post("/raw-input")
async def log_raw_input(raw_data: RawInputData):
    """
    Log raw form input without AI results to Google Sheets
    
    Example request:
    {
        "age": 25,
        "gender": "หญิง",
        "hn": "12345",
        ...any other form fields
    }
    """
    try:
        # Convert Pydantic model to dict
        form_data = raw_data.model_dump()
        append_raw_input(form_data, FORM_COLUMNS)
        
        logger.info("Successfully logged raw input")
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to log raw input: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to log raw input: {str(e)}"
        )
