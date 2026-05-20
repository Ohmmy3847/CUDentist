"""
Patient Assessment Router - Comprehensive Risk Assessment Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
import logging
import asyncio

from app.models.schemas import PatientData
from app.services.risk.summarizer import summarize_all_risks
from app.services.risk.flow_parser import RuleEngine
from app.core.config import settings
from app.core.dependencies import get_llm


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["patient-assessment"]
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
            "/patient-assessment": "POST - Comprehensive patient risk assessment (2-layer system: Rule-based + LLM Summary)",
            "/flows": "GET - List available flows"
        }
    }


@router.get("/flows")
async def get_flows():
    """Get list of available risk classification flows"""
    return {"flows": RuleEngine.get_flow_names()}


@router.post("/patient-assessment")
async def comprehensive_patient_assessment(patient: PatientData, llm = Depends(get_llm)):
    """
    Comprehensive Patient Risk Assessment - 2-Layer System:
    1. RuleEngine - Deterministic classification for structured data
    2. LLM Summarizer - Comprehensive summary and recommendations
    
    Example request:
    {
        "basic_info": {
            "first_name": "สมชาย",
            "last_name": "ใจดี",
            "birth_date": "2000-05-15",
            "hn": "HN12345",
            "procedures": ["BSSRO"],
            "surgery_date": "2026-01-09"
        },
        "assessment_data": {
            "pain_score": 5,
            "pain_medication_effect": "ดีขึ้น",
            "swelling_description": "บวมมากแต่ยังทนได้"
        },
        "language": "th"
    }
    
    Returns:
    {
        "patient": {...},  # Patient info and assessment data
        "flows": {...},  # Individual flow results (Rule-based)
        "summary": {...},  # Overall summary and recommendations
        "errors": {...}  # Errors if any
    }
    """
    logger.info(f"Received comprehensive patient assessment request")
    logger.info(f"Basic info: {patient.basic_info.first_name} {patient.basic_info.last_name}, HN: {patient.basic_info.hn}")
    logger.info(f"Assessment data keys: {list(patient.assessment_data.keys())}")
    logger.info(f"Patient Language: '{patient.language}' (Type: {type(patient.language)})")
    
    # Merge basic_info and assessment_data for processing
    merged_data = {**patient.basic_info.dict(exclude_none=True), **patient.assessment_data}
    
    results = {}
    errors = {}

    language = patient.language or "th"

    async def process_flow(flow_name: str):
        """Process a single flow asynchronously with RuleEngine"""
        try:
            logger.info(f"Processing flow: {flow_name}")
            engine = RuleEngine()

            if flow_name == "other_symptoms_custom_flow":
                temp_data = merged_data.copy()
                temp_data['other_symptoms'] = []
                result = await asyncio.to_thread(
                    engine.evaluate_flow,
                    "other_symptoms",
                    temp_data,
                    language=language
                )
            # Check if this is a dynamically created symptom flow
            # (not in original flow_names, meaning it's from other_symptoms expansion)
            elif flow_name not in flow_names_set:
                # This is a standard symptom - evaluate using evaluate_other_symptoms logic
                # Create temporary data with single symptom
                temp_data = merged_data.copy()
                temp_data['other_symptoms'] = [flow_name]
                temp_data['other_symptoms_custom'] = ''
                
                result = await asyncio.to_thread(
                    engine.evaluate_flow,
                    "other_symptoms",
                    temp_data,
                    language=language
                )
            else:
                # Normal flow
                result = await asyncio.to_thread(
                    engine.evaluate_flow,
                    flow_name,
                    merged_data,
                    language=language
                )
            
            logger.info(f"Successfully processed flow: {flow_name}")
            
            if isinstance(result, dict) and result.get('is_multiple_flows'):
                flows = []
                flows_data = result.get('flows', {})
                if isinstance(flows_data, dict):
                    for fname, res in flows_data.items():
                        flows.append((fname, res, None))
                else:
                    logger.error(f"Expected 'flows' to be a dict, got {type(flows_data)}: {repr(flows_data)}")
                    flows.append((flow_name, result, f"Invalid 'flows' type: {type(flows_data)}"))
                return flows
            else:
                return [(flow_name, result, None)]
        except Exception as flow_error:
            logger.error(f"Error in flow {flow_name}: {str(flow_error)}", exc_info=True)
            return [(flow_name, None, str(flow_error))]

    try:
        # Phase 1: Rule-based classification (parallel)
        logger.info("Phase 1: Running rule-based classification...")
        flow_names = RuleEngine.get_flow_names()
        flow_names_set = set(flow_names)
        
        # Auto-expand "other_symptoms" into individual flows
        expanded_flows = []
        
        for flow_name in flow_names:
            if flow_name == "other_symptoms":
                # Get selected symptoms from choices
                other_symptoms = merged_data.get('other_symptoms', [])
                if isinstance(other_symptoms, list) and other_symptoms:
                    # Create individual flow for each symptom
                    for symptom in other_symptoms:
                        expanded_flows.append(symptom.strip())
                
                # Check for custom symptoms (ผู้ป่วยพิมพ์เอง)
                custom_symptoms = merged_data.get('other_symptoms_custom', '')
                logger.info(f"Custom symptoms: {custom_symptoms}")
                if isinstance(custom_symptoms, list):
                    custom_symptoms = ', '.join(str(item.get('symptom', item)) if isinstance(item, dict) else str(item) for item in custom_symptoms if item)
                
                if custom_symptoms:
                    expanded_flows.append("other_symptoms_custom_flow")
                
                # Skip the original "other_symptoms" flow
            else:
                expanded_flows.append(flow_name)

        logger.info(f"Expanded flows: {expanded_flows}")
        
        tasks = [process_flow(flow_name) for flow_name in expanded_flows]
            
        flow_results_lists = await asyncio.gather(*tasks)
        
        # Collect results and errors
        for flow_results in flow_results_lists:
            for flow_name, result, error in flow_results:
                if result:
                    results[flow_name] = result
                if error:
                    errors[flow_name] = error
                
        if not results and errors:
            raise HTTPException(
                status_code=500, 
                detail=f"All flows failed. Errors: {errors}"
            )
        
        # Phase 2: LLM summarization (สรุปเหตุผลและคำแนะนำโดยรวม)
        logger.info("Phase 2: Generating overall summary with LLM...")
        procedures = merged_data.get('procedures', merged_data.get('procedure', 'ไม่ระบุ'))
        
        summary = await asyncio.to_thread(
            summarize_all_risks,
            all_results=results,
            llm=llm,
            patient_data=patient.basic_info.dict(exclude_none=True),
            procedures=procedures,
            language=language
        )
        
        # Phase 3: Patient Question (RAG)
        qa_answer_dict = None
        patient_question = (
            getattr(patient, 'patient_question', None)
            or patient.assessment_data.get("additional_questions", "")
        )
        
        if patient_question and patient_question.strip():
            logger.info(f"Phase 3: Processing patient question with RAG: '{patient_question[:60]}...'")
            from app.services.rag.pipeline import answer_patient_question
            from app.services.rag.context_builder import build_patient_context
            
            # Build rich context from all assessment data
            patient_context = build_patient_context(
                basic_info=patient.basic_info.dict(exclude_none=True),
                assessment_data=patient.assessment_data,
                flows=results,
                summary={
                    "overall_risk": summary.overall_risk,
                    "summary": summary.summary
                }
            )
            
            qa_answer_dict = await answer_patient_question(
                question=patient_question.strip(),
                patient_context=patient_context
            )
        
        # Compile final response
        response = {
            "patient": {"basic_info": patient.basic_info.dict(exclude_none=True), "assessment_data": patient.assessment_data},
            "flows": results,
            "language": patient.language,
            # "descriptions": description_analysis,
            "summary": {
                "overall_risk": summary.overall_risk,
                "summary": summary.summary
            },
            "qa_answer": {k: v for k, v in (qa_answer_dict or {}).items() if k != "used_chunks"} if qa_answer_dict else None,
            "qa_chunks": qa_answer_dict.get("used_chunks") if qa_answer_dict else None,
            "errors": errors if errors else None
        }
        
        logger.info(f"Classification completed successfully. Overall risk: {summary.overall_risk}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Classification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")
