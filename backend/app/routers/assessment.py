"""
Patient Assessment Router - Comprehensive Risk Assessment Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
import logging
import asyncio

from app.models.schemas import PatientData
from app.services.risk_service import (
    classify_risk,
    FORM_COLUMNS,
    FIELD_LABELS,
    summarize_all_risks,
)
from app.core.constants import FIELD_WITH_DESCRIPTION, DESCRIPTION_LABELS
from app.services.flow_parser import RuleEngine
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


    async def process_flow(flow_name: str, flow: str):
        """Process a single flow asynchronously with RuleEngine"""
        try:
            logger.info(f"Processing flow: {flow_name}")
            
            # Check if this is a dynamically created symptom flow
            # (not in original flow_names, meaning it's from other_symptoms expansion)
            if flow_name not in RuleEngine.get_flow_names():
                # Check if it's a custom symptom (starts with "custom_symptom:")
                if flow_name.startswith("custom_symptom:"):
                    # Extract the custom symptoms text
                    custom_text = flow_name.replace("custom_symptom:", "").strip()
                    
                    # Create temporary data with custom symptoms
                    temp_data = merged_data.copy()
                    temp_data['other_symptoms'] = []  # Clear standard symptoms
                    temp_data['other_symptoms_custom'] = custom_text
                    
                    result = await asyncio.to_thread(
                        classify_risk,
                        input_data=temp_data,
                        flow=flow,
                        flow_name="other_symptoms",  # Use original flow for evaluation
                        llm=llm,
                        language=patient.language
                    )
                else:
                    # This is a standard symptom - evaluate using evaluate_other_symptoms logic
                    # Create temporary data with single symptom
                    temp_data = merged_data.copy()
                    temp_data['other_symptoms'] = [flow_name]
                    temp_data['other_symptoms_custom'] = ''  # Clear custom to avoid COMPLICATED
                    
                    result = await asyncio.to_thread(
                        classify_risk,
                        input_data=temp_data,
                        flow=flow,
                        flow_name="other_symptoms",  # Use original flow for evaluation
                        llm=llm,
                        language=patient.language
                    )
            else:
                # Normal flow
                result = await asyncio.to_thread(
                    classify_risk,
                    input_data=merged_data,
                    flow=flow,
                    flow_name=flow_name,
                    llm=llm,
                    language=patient.language
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
    
    async def _analyze_standard_description_field(
        main_field: str,
        desc_field: str,
        patient_data: dict,
        llm
    ) -> tuple:
        """
        วิเคราะห์ description field เดี่ยวด้วย LLM
        
        Returns:
            tuple: (desc_field, result_dict) หรือ (None, None) ถ้าไม่มีข้อมูล
        """
        description = patient_data.get(desc_field, "")
        main_value = patient_data.get(main_field, "ไม่ระบุ")
        
        if not description or not description.strip():
            return None, None
        
        # Get labels
        main_field_label = FIELD_LABELS.get(main_field, main_field)
        desc_field_label = DESCRIPTION_LABELS.get(desc_field, desc_field)
        
        # Get procedures
        procedures = patient_data.get('procedures', patient_data.get('procedure', 'ไม่ระบุ'))
        
        # Analyze with LLM
        analysis = await asyncio.to_thread(
            main_field_label,
            desc_field_label,
            description,
            str(main_value),
            procedures,
            llm
        )
        
        result = {
            'field': desc_field_label,
            'main_field': main_field_label,
            'description': description,
            'main_value': main_value,
            'analysis': {
                'has_risk': analysis.has_risk,
                'risk_level': analysis.risk_level,
                'analysis': analysis.analysis,
                'key_points': analysis.key_points
            } if hasattr(analysis, 'has_risk') else analysis
        }
        
        return desc_field, result
    
    async def _analyze_custom_text_field(
        field_name: str,
        field_label: str,
        patient_data: dict,
        llm
    ) -> tuple:
        """
        วิเคราะห์ custom text field (array หรือ string) ด้วย LLM
        
        Returns:
            tuple: (field_name, result_dict) หรือ (None, None) ถ้าไม่มีข้อมูล
        """
        custom_values = patient_data.get(field_name)
        if not custom_values:
            return None, None
        
        # Get procedures
        procedures = patient_data.get('procedures', patient_data.get('procedure', 'ไม่ระบุ'))
        
        # Analyze with LLM
        analysis = await asyncio.to_thread(
            field_label,
            field_label,
            custom_values,
            "ผู้ป่วยระบุเพิ่มเติม",
            procedures,
            llm
        )
        
        result = {
            'field': field_label,
            'main_field': field_label,
            'description': custom_values,
            'main_value': "ผู้ป่วยระบุเพิ่มเติม",
            'analysis': {
                'has_risk': analysis.has_risk,
                'risk_level': analysis.risk_level,
                'analysis': analysis.analysis,
                'key_points': analysis.key_points
            } if hasattr(analysis, 'has_risk') else analysis
        }
        
        return field_name, result
    
        """
        วิเคราะห์ description fields และ custom text fields ด้วย LLM (parallel)
        
        Returns:
            dict: ผลการวิเคราะห์ทั้งหมด {field_name: result}
        """
        tasks = []
        
        # 1. สร้าง tasks สำหรับ standard description fields
        for main_field, desc_field in FIELD_WITH_DESCRIPTION.items():
            if desc_field in merged_data:
                tasks.append(_analyze_standard_description_field(
                    main_field, desc_field, merged_data, llm
                ))
        
        # 2. สร้าง tasks สำหรับ custom text fields
        from app.core.constants import CUSTOM_TEXT_FIELDS
        for field_name, field_label in CUSTOM_TEXT_FIELDS.items():
            if field_name in merged_data:
                tasks.append(_analyze_custom_text_field(
                    field_name, field_label, merged_data, llm
                ))
        
        # 3. รัน LLM analysis แบบ parallel
        if not tasks:
            return {}
        
        results = await asyncio.gather(*tasks)
        
        # 4. รวบรวมผลลัพธ์
        desc_results = {}
        for field_name, result in results:
            if result:
                desc_results[field_name] = result
        
        return desc_results

    try:
        # Phase 1: Rule-based classification (parallel)
        logger.info("Phase 1: Running rule-based classification...")
        flow_names = RuleEngine.get_flow_names()
        
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
                if isinstance(custom_symptoms, list):
                    custom_symptoms = ', '.join(str(item) for item in custom_symptoms if item)
                custom_symptoms = str(custom_symptoms).strip()
                
                if custom_symptoms:
                    # Create special flow for custom symptoms
                    expanded_flows.append(f"custom_symptom:{custom_symptoms}")
                
                # Skip the original "other_symptoms" flow
            else:
                expanded_flows.append(flow_name)
        
        tasks = [process_flow(flow_name, None) for flow_name in expanded_flows]
        flow_results = await asyncio.gather(*tasks)
        
        # Collect results and errors
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
            language=patient.language
        )
        
        # Compile final response
        response = {
            "patient": {"basic_info": patient.basic_info.dict(exclude_none=True), "assessment_data": patient.assessment_data},
            "flows": results,
            "language": patient.language,
            # "descriptions": description_analysis,
            "summary": {
                "overall_risk": summary.overall_risk,
                "critical_issues": summary.critical_issues,
                "summary": summary.summary
            },
            "errors": errors if errors else None
        }
        
        logger.info(f"Classification completed successfully. Overall risk: {summary.overall_risk}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Classification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

