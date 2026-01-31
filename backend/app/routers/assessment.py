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
    analyze_description_field,
    summarize_all_risks,
    answer_patient_questions,
    FIELD_WITH_DESCRIPTION,
    DESCRIPTION_LABELS
)
from app.services.log_service import append_with_result
from app.core.flows import FLOWS
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global variable to hold get_llm function (set by main.py)
get_llm = None

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
            "/patient-assessment": "POST - Comprehensive patient risk assessment (3-layer system)",
            "/flows": "GET - List available flows"
        }
    }


@router.get("/flows")
async def get_flows():
    """Get list of available risk classification flows"""
    return {"flows": list(FLOWS.keys())}


@router.post("/patient-assessment")
async def comprehensive_patient_assessment(patient: PatientData, llm = Depends(lambda: get_llm())):
    """
    Comprehensive Patient Risk Assessment - 3-Layer System:
    1. RuleEngine - Deterministic classification for structured data
    2. LLM Analyzer - Analyze free-text description fields
    3. LLM Summarizer - Comprehensive summary + answer patient questions
    
    Example request:
    {
        "basic_info": {
            "first_name": "สมชาย",
            "last_name": "ใจดี",
            "age": 35,
            "hn": "HN12345",
            "procedures": ["BSSRO"],
            "surgery_date": "2026-01-09"
        },
        "assessment_data": {
            "pain_score": 5,
            "pain_medication_effect": "ดีขึ้น",
            "swelling_description": "บวมมากแต่ยังทนได้",
            "additional_questions": "ควรประคบนานแค่ไหน?"
        }
    }
    
    Returns:
    {
        "flows": {...},  # Individual flow results (Rule-based)
        "descriptions": {...},  # LLM analysis of free-text fields
        "summary": {...},  # Overall summary and recommendations
        "patient_qa": "..."  # Answer to patient's questions
    }
    """
    logger.info(f"Received comprehensive patient assessment request")
    logger.info(f"Basic info: {patient.basic_info.first_name} {patient.basic_info.last_name}, HN: {patient.basic_info.hn}")
    logger.info(f"Assessment data keys: {list(patient.assessment_data.keys())}")
    
    # Merge basic_info and assessment_data for processing
    merged_data = {**patient.basic_info.dict(exclude_none=True), **patient.assessment_data}
    
    results = {}
    errors = {}
    description_analysis = {}

    async def process_flow(flow_name: str, flow: str):
        """Process a single flow asynchronously with RuleEngine"""
        try:
            logger.info(f"Processing flow: {flow_name}")
            # Run classify_risk in thread pool since it's synchronous
            result = await asyncio.to_thread(
                classify_risk,
                input_data=merged_data,
                flow=flow,
                flow_name=flow_name,
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
            analyze_description_field,
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
            analyze_description_field,
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
    
    async def analyze_descriptions():
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
        tasks = [process_flow(flow_name, flow) for flow_name, flow in FLOWS.items()]
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
        
        # Phase 2: LLM analysis of description fields
        # logger.info("Phase 2: Analyzing description fields with LLM...")
        # description_analysis = await analyze_descriptions()
        
        # Phase 3: LLM summarization (สรุบเหตุผลและคำแนะนำ รวม context จาก description analysis)
        logger.info("Phase 3: Generating overall summary with LLM...")
        procedures = merged_data.get('procedures', merged_data.get('procedure', 'ไม่ระบุ'))
        
        summary = await asyncio.to_thread(
            summarize_all_risks,
            results,
            llm,
            patient.basic_info.dict(exclude_none=True),
            # description_analysis,  # เพิ่ม description analysis context
            procedures            # เพิ่ม procedures context
        )
        
        # Phase 4: Answer patient questions (if any)
        patient_qa = None
        additional_questions = merged_data.get('additional_questions', '')
        if additional_questions and additional_questions.strip():
            logger.info("Phase 4: Answering patient questions with LLM...")
            patient_qa = await asyncio.to_thread(
                answer_patient_questions,
                additional_questions,
                patient.basic_info.dict(exclude_none=True),
                llm,
                results,      # เพิ่ม risk results เป็น context
                procedures    # เพิ่ม procedures context
            )
        
        # Compile final response
        response = {
            "patient": {"basic_info": patient.basic_info.dict(exclude_none=True), "assessment_data": patient.assessment_data},
            "flows": results,
            
            # "descriptions": description_analysis,
            "summary": {
                "overall_risk": summary.overall_risk,
                "critical_issues": summary.critical_issues,
                "summary": summary.summary
            },
            "patient_qa": {
                "answer": patient_qa.answer,
                "urgency_level": patient_qa.urgency_level,
                "should_contact_doctor": patient_qa.should_contact_doctor,
                "related_risks": patient_qa.related_risks
            } if patient_qa else None,
            "errors": errors if errors else None
        }
        
        logger.info(f"Classification completed successfully. Overall risk: {summary.overall_risk}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Classification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

