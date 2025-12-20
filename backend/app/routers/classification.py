"""
Classification Router - Risk Assessment Endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
import pandas as pd
import os
import logging
import asyncio
from datetime import datetime

from app.models.schemas import PatientData, RiskResponse
from app.services.risk_service import classify_risk, _process_all_rows, FORM_COLUMNS
from app.services.log_service import append_with_result
from app.core.flows import FLOWS
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global variable to hold get_llm function (set by main.py)
get_llm = None

router = APIRouter(
    prefix="",
    tags=["classification"]
)


@router.get("/")
async def root():
    """
    Root endpoint. Returns API information.
    """
    return {
        "message": settings.API_TITLE,
        "version": settings.API_VERSION,
        "endpoints": {
            "/classify": "POST - Classify single patient data",
            "/classify-all-flows": "POST - Classify with all flows",
            "/classify-csv": "POST - Upload and process CSV file",
            "/flows": "GET - List available flows"
        }
    }


@router.get("/flows")
async def get_flows():
    """Get list of available risk classification flows"""
    return {"flows": list(FLOWS.keys())}


@router.post("/classify", response_model=RiskResponse)
async def classify_patient(patient: PatientData, llm = Depends(lambda: get_llm())):
    """
    Classify risk for a single patient
    
    Example request:
    {
        "data": {"symptom": "ปวดหัว", "duration": "3 days"},
        "flow_name": "head_pain"
    }
    """
    logger.info(f"Using Model: {settings.MODEL_NAME}")
    
    if patient.flow_name and patient.flow_name not in FLOWS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid flow_name. Available: {list(FLOWS.keys())}"
        )
    
    flow_name = patient.flow_name or list(FLOWS.keys())[0]
    flow = FLOWS[flow_name]
    
    try:
        result = classify_risk(
            input_data=patient.data,
            flow=flow,
            llm=llm
        )
        return RiskResponse(
            risk_level=result.risk_level,
            recommendation=result.recommendation,
            reason=result.reason
        )
    except Exception as e:
        logger.error(f"Classification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")


@router.post("/classify-all-flows")
async def classify_all_flows(patient: PatientData, llm = Depends(lambda: get_llm())):
    """
    Classify risk for a single patient across all flows (parallel processing)
    
    Example request:
    {
        "data": {"symptom": "ปวดหัว", "duration": "3 days"}
    }
    """
    logger.info(f"Received classify-all-flows request with data keys: {list(patient.data.keys())}")
    results = {}
    errors = {}

    async def process_flow(flow_name: str, flow: str):
        """Process a single flow asynchronously"""
        try:
            logger.info(f"Processing flow: {flow_name}")
            # Run classify_risk in thread pool since it's synchronous
            result = await asyncio.to_thread(
                classify_risk,
                input_data=patient.data,
                flow=flow,
                llm=llm
            )
            logger.info(f"Successfully processed flow: {flow_name}")
            return flow_name, {
                "risk_level": result.risk_level,
                "recommendation": result.recommendation,
                "reason": result.reason
            }, None
        except Exception as flow_error:
            logger.error(f"Error in flow {flow_name}: {str(flow_error)}", exc_info=True)
            return flow_name, None, str(flow_error)

    try:
        # Process all flows in parallel
        tasks = [process_flow(flow_name, flow) for flow_name, flow in FLOWS.items()]
        flow_results = await asyncio.gather(*tasks)
        
        # Collect results and errors
        for flow_name, result, error in flow_results:
            if result:
                results[flow_name] = result
            if error:
                errors[flow_name] = error
                
        if not results and errors:
            # All flows failed
            raise HTTPException(
                status_code=500, 
                detail=f"All flows failed. Errors: {errors}"
            )
        
        # Log results to Google Sheets
        if results:
            try:
                append_with_result(patient.data, results, FORM_COLUMNS)
                logger.info("Successfully logged results to Google Sheets")
            except Exception as log_error:
                logger.warning(f"Failed to log to Google Sheets: {str(log_error)}")
        
        # Return only results (compatible with frontend)
        if errors:
            logger.warning(f"Some flows failed: {list(errors.keys())}")
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Classification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")


@router.post("/classify-csv")
async def classify_csv(
    file: UploadFile = File(...),
    max_concurrent: int = 10,
    llm = None
):
    """
    Upload CSV file and process all rows
    Returns the processed file
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV format")
    
    # Save uploaded file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = f"temp_input_{timestamp}.csv"
    output_path = f"result_{timestamp}.csv"
    
    try:
        # Save uploaded file
        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Read CSV and prepare dataframe
        df = pd.read_csv(input_path)
        for flow_name in FLOWS.keys():
            df[f"{flow_name}_risk_level"] = ""
            df[f"{flow_name}_risk_reason"] = ""
            df[f"{flow_name}_recommendation"] = ""
        
        # Process CSV asynchronously
        await _process_all_rows(df, llm, output_path, max_concurrent)
        
        # Clean up input file
        os.remove(input_path)
        
        # Return processed file
        return FileResponse(
            path=output_path,
            filename=f"risk_classification_{timestamp}.csv",
            media_type="text/csv"
        )
    except Exception as e:
        # Clean up on error
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        logger.error(f"CSV processing error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
