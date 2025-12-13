from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Optional, Any
import pandas as pd
import os
import logging
from datetime import datetime

from riskClassification import classify_risk, csv_to_risk_classification, build_llm, _process_all_rows
from flow import FLOWS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Risk Classification API")

# Add CORS middleware
FRONTEND_URL = os.getenv("FRONTEND_URL", "")
allowed_origins = [
    "http://localhost:3000", 
    "http://localhost:3001",
    "https://cudent-e3utbty62-ohmmy3847s-projects.vercel.app",  # Production
    "https://cudent.vercel.app",  # Custom domain (if any)
]
if FRONTEND_URL and FRONTEND_URL not in allowed_origins:
    allowed_origins.append(FRONTEND_URL)

# Allow all Vercel preview deployments
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global LLM instance
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")
os.environ["GOOGLE_API_KEY"] = API_KEY
llm = build_llm(API_KEY)

# Request/Response Models
class PatientData(BaseModel):
    data: Dict[str, Any]
    flow_name: Optional[str] = None  # ถ้าไม่ระบุจะรันทุก flow

class RiskResponse(BaseModel):
    risk_level: str
    recommendation: str
    reason: str

@app.get("/")
async def root():
    return {
        "message": "Risk Classification API",
        "endpoints": {
            "/classify": "POST - Classify single patient data",
            "/classify-all-flows": "POST - Classify with all flows",
            "/classify-csv": "POST - Upload and process CSV file",
            "/flows": "GET - List available flows"
        }
    }

@app.get("/flows")
async def get_flows():
    """Get list of available risk classification flows"""
    return {"flows": list(FLOWS.keys())}

@app.post("/classify", response_model=RiskResponse)
async def classify_patient(patient: PatientData):
    """
    Classify risk for a single patient
    
    Example request:
    {
        "data": {"symptom": "ปวดหัว", "duration": "3 days"},
        "flow_name": "head_pain"
    }
    """
    if patient.flow_name and patient.flow_name not in FLOWS:
        raise HTTPException(status_code=400, detail=f"Invalid flow_name. Available: {list(FLOWS.keys())}")
    
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
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

@app.post("/classify-all-flows")
async def classify_all_flows(patient: PatientData):
    """
    Classify risk for a single patient across all flows
    
    Example request:
    {
        "data": {"symptom": "ปวดหัว", "duration": "3 days"}
    }
    """
    logger.info(f"Received classify-all-flows request with data keys: {list(patient.data.keys())}")
    results = {}
    errors = {}
    
    try:
        for flow_name, flow in FLOWS.items():
            try:
                logger.info(f"Processing flow: {flow_name}")
                result = classify_risk(
                    input_data=patient.data,
                    flow=flow,
                    llm=llm
                )
                results[flow_name] = {
                    "risk_level": result.risk_level,
                    "recommendation": result.recommendation,
                    "reason": result.reason
                }
                logger.info(f"Successfully processed flow: {flow_name}")
            except Exception as flow_error:
                logger.error(f"Error in flow {flow_name}: {str(flow_error)}", exc_info=True)
                errors[flow_name] = str(flow_error)
                # Continue with other flows
                
        if not results and errors:
            # All flows failed
            raise HTTPException(
                status_code=500, 
                detail=f"All flows failed. Errors: {errors}"
            )
        
        # Return only results (compatible with frontend)
        # Log errors separately but don't include in response
        if errors:
            logger.warning(f"Some flows failed: {list(errors.keys())}")
            
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Classification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

@app.post("/classify-csv")
async def classify_csv(
    file: UploadFile = File(...),
    max_concurrent: int = 10
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
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
