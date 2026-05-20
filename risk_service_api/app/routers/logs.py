"""
Logging Router - Form Submission Logging Endpoints
"""
from fastapi import APIRouter, HTTPException
import logging
from datetime import datetime

from app.models.schemas import LogData, RawInputData

from app.core.constants import FORM_COLUMNS

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/log",
    tags=["logging"]
)


@router.post("/submission")
async def log_form_submission(log_data: LogData):
    """
    Log form submission to Google Sheets
    
    Supports both legacy and new 3-layer response formats:
    - Legacy: {"อาการปวด": {"risk_level": "...", ...}}
    - New: {"flows": {...}, "descriptions": {...}, "summary": {...}}
    
    Example request:
    {
        "form_data": {"age": 25, "gender": "หญิง", ...},
        "results": {"flows": {...}, "summary": {...}},  // New format
        "session_id": "user_123"
    }
    """
    try:
        timestamp = datetime.now().isoformat()
        
        # Check if results is new 3-layer format or legacy format
        results_to_log = log_data.results
        if "flows" in log_data.results:
            # New format - extract flows for backward compatibility with Google Sheets
            logger.info("Detected new 3-layer format, extracting flows")
            results_to_log = log_data.results["flows"]
        else:
            # Legacy format - use as-is
            logger.info("Using legacy format")
        
      
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

