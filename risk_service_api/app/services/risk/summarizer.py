"""
Risk Summarization Service

LLM-based summarization functions:
- summarize_all_risks: สรุปผลการประเมินจากทุก flows
- answer_patient_questions: ตอบคำถามผู้ป่วยด้วย LLM
"""
import logging
from typing import List, Dict, Any

from langchain_core.output_parsers import PydanticOutputParser

from app.core.constants import FLOW_TOPIC_NAMES, PHONE_NUMBER
from app.models.schemas import (
    RiskSummaryContent,
    RiskSummaryOutput,
    PatientQuestionAnswer,
)
from app.services.common.prompts import (
    build_high_risk_prompt,
    build_medium_risk_prompt,
    build_patient_question_prompt,
)
from app.services.risk.risk_helpers import (
    categorize_risks_by_level,
    calculate_overall_risk,
    normalize_topic,
    extract_recommendations_from_flows,
    format_high_risk_message,
    format_medium_risk_message,
    format_low_risk_message,
    format_complex_case_message,
    parse_llm_json,
    generate_fallback_summary_text,
)

logger = logging.getLogger(__name__)


_RISK_HIGH = frozenset(['High Risk', 'ความเสี่ยงสูง'])
_RISK_MEDIUM = frozenset(['Medium Risk', 'ความเสี่ยงปานกลาง'])
_RISK_LOW = frozenset(['Low Risk', 'ความเสี่ยงต่ำ'])
_RISK_COMPLICATED = frozenset(['Complicated', 'ซับซ้อน'])


# ------------------------------------------------------------
# Patient Summary Generation (LLM + Rule-based formatting)
# ------------------------------------------------------------

def _generate_patient_summary(
    overall_risk: str,
    high_risk: List[str],
    medium_risk: List[str],
    high_risk_flows: List[tuple],
    medium_risk_flows: List[tuple],
    low_risk_flows: List[tuple],
    patient_name: str,
    llm,
    language: str = 'th'
) -> str:
    """
    สร้าง summary สำหรับผู้ป่วย
    - LLM: สรุปสาเหตุ (risk_summary) → return JSON
    - Python: ดึง recommendations จาก Rule Engine โดยตรง + จัด format ข้อความ 100%
    """
    if language == 'en':
        name_text = f"{patient_name}" if patient_name else "the patient"
    else:
        name_text = f"คุณ{patient_name}" if patient_name else ""

    # Rule-based: ดึง recommendations จาก flows โดยตรง
    high_recs = extract_recommendations_from_flows(high_risk_flows, language)
    medium_recs = extract_recommendations_from_flows(medium_risk_flows, language)
    low_recs = extract_recommendations_from_flows(low_risk_flows, language)

    try:
        parser = PydanticOutputParser(pydantic_object=RiskSummaryContent)

        if overall_risk in _RISK_HIGH:
            other_recs = medium_recs + low_recs
            prompt = build_high_risk_prompt(
                high_risk=high_risk,
                language=language,
                format_instructions=parser.get_format_instructions()
            )
            print("\n" + "="*80)
            print(f"📝 PROMPT: _generate_patient_summary (high risk)")
            print("="*80)
            print(prompt)
            print("="*80 + "\n")
            response = llm.invoke(prompt)
            content = parse_llm_json(parser, response.content)
            return format_high_risk_message(content.risk_summary, high_recs, other_recs, name_text, language)

        elif overall_risk in _RISK_MEDIUM:
            other_recs = low_recs
            prompt = build_medium_risk_prompt(
                medium_risk=medium_risk,
                language=language,
                format_instructions=parser.get_format_instructions()
            )
            print("\n" + "="*80)
            print(f"📝 PROMPT: _generate_patient_summary (medium risk)")
            print("="*80)
            print(prompt)
            print("="*80 + "\n")
            response = llm.invoke(prompt)
            content = parse_llm_json(parser, response.content)
            return format_medium_risk_message(content.risk_summary, medium_recs, other_recs, name_text, language)

        elif overall_risk in _RISK_LOW:
            return format_low_risk_message(
                 risk_summary="ไม่พบความเสี่ยงที่มีนัยสำคัญ" if language == 'th' else "No significant risks found.",
                 all_recs=low_recs,
                 name_text=name_text,
                 language=language
            )

    except Exception as e:
        print(f"Error generating patient summary: {e}")
        
        fallback_recs = []
        fallback_reasons = []
        if overall_risk in _RISK_HIGH:
            fallback_recs = high_recs + medium_recs + low_recs
            fallback_reasons = high_risk
        elif overall_risk in _RISK_MEDIUM:
            fallback_recs = medium_recs + low_recs
            fallback_reasons = medium_risk
        elif overall_risk in _RISK_LOW:
            fallback_recs = low_recs
            fallback_reasons = []
            
        return generate_fallback_summary_text(
            overall_risk=overall_risk,
            name_text=name_text,
            language=language,
            reasons=fallback_reasons,
            all_recs=fallback_recs
        )


def _create_fallback_summary(
    overall_risk: str,
    high_risk: List[str],
    medium_risk: List[str],
    low_risk: List[str],
    high_risk_flows: List[tuple],
    medium_risk_flows: List[tuple],
    low_risk_flows: List[tuple],
    language: str = 'th'
) -> RiskSummaryOutput:
    """สร้าง fallback summary เมื่อ LLM ไม่พร้อมใช้งาน"""
    
    patient_summary_parts = []
    if high_risk:
        patient_summary_parts.append(f"พบความเสี่ยงสูง {len(high_risk)} รายการ ต้องดูแลอย่างใกล้ชิด")
    if medium_risk:
        patient_summary_parts.append(f"มีความเสี่ยงปานกลาง {len(medium_risk)} รายการ")
    
    rec_parts = []
    for flow_name, result in high_risk_flows:
        if result['recommendation']:
            rec_parts.append(result['recommendation'])
    for flow_name, result in medium_risk_flows:
        if result['recommendation']:
            rec_parts.append(result['recommendation'])
    for flow_name, result in low_risk_flows:
         if result['recommendation']:
             rec_parts.append(result['recommendation'])

    if patient_summary_parts:
        summary = " ".join(patient_summary_parts)
        if rec_parts:
            summary += (" Recommendation: " if language == 'en' else " คำแนะนำ: ") + " ".join(rec_parts[:3])
    else:
        base_msg = "Symptoms are normal." if language == 'en' else "อาการอยู่ในเกณฑ์ปกติ"
        if rec_parts:
             recs_str = " ".join(rec_parts[:3])
             summary = f"{base_msg} {recs_str}"
        else:
             summary = "Symptoms are normal. Follow doctor's advice." if language == 'en' else "อาการอยู่ในเกณฑ์ปกติ ดูแลตามคำแนะนำจากแพทย์"
    
    return RiskSummaryOutput(
        overall_risk=overall_risk,
        summary=summary,
    )


# ------------------------------------------------------------
# Main Summarization Function
# ------------------------------------------------------------

def summarize_all_risks(
    all_results: Dict[str, Dict[str, str]], 
    llm, 
    patient_data: dict = None,
    procedures: str = None,
    language: str = 'th'
) -> RiskSummaryOutput:
    """
    สรุปผลการประเมินจากทุก flows โดยใช้ rule-based คำนวณ overall risk 
    และใช้ LLM สรุป "เหตุผล" และ "คำแนะนำ"
    """

    # 0. Translate flow names if language is English
    if language == 'en':
        translated_results = {}
        for flow_name, result in all_results.items():
            entry = FLOW_TOPIC_NAMES.get(flow_name)
            translated_name = entry['en'] if entry else flow_name
            translated_results[translated_name] = result
        all_results = translated_results

    # 1. แยกตามระดับความเสี่ยง
    (high_risk, high_risk_flows, medium_risk, 
     medium_risk_flows, low_risk, low_risk_flows,
     complicated_risk, complicated_risk_flows) = categorize_risks_by_level(all_results, language)
    
    # 2. คำนวณความเสี่ยงโดยรวม (Rule-based)
    overall_risk = calculate_overall_risk(len(high_risk), len(medium_risk), len(complicated_risk), language)
    
    # 4. ดึงชื่อผู้ป่วย
    patient_name = ""
    if patient_data and isinstance(patient_data, dict):
        first_name = patient_data.get('first_name', '')
        last_name = patient_data.get('last_name', '')
        if first_name or last_name:
            patient_name = f"{first_name}".strip()
    
    # 5. ถ้าไม่มี LLM ให้ใช้ fallback
    if not llm:
        return _create_fallback_summary(
            overall_risk, high_risk, medium_risk, low_risk,
            high_risk_flows, medium_risk_flows, low_risk_flows,
            language
        )
    
    # 6. Optimization: Skip LLM for Low and Complicated risks
    if overall_risk in _RISK_LOW or overall_risk in _RISK_COMPLICATED:
        print(f"Skipping LLM for {overall_risk} risk")

        summary = ""
        if overall_risk in _RISK_LOW:
            low_recs = extract_recommendations_from_flows(low_risk_flows, language)
            summary = format_low_risk_message(
                risk_summary="ไม่พบความเสี่ยงที่มีนัยสำคัญ" if language == 'th' else "No significant risks found.",
                all_recs=low_recs,
                name_text=f"คุณ{patient_name}" if patient_name else "ผู้ป่วย",
                language=language
            )
        else:  # Complicated
            low_recs = extract_recommendations_from_flows(low_risk_flows, language)
            summary = format_complex_case_message(
                risk_summary="",
                all_recs=low_recs,
                language=language
            )
            
        return RiskSummaryOutput(
            overall_risk=overall_risk,
            summary=summary,
        )

    # 7. เรียก LLM สร้าง summary
    try:
        summary = _generate_patient_summary(
            overall_risk, high_risk, medium_risk,
            high_risk_flows, medium_risk_flows, low_risk_flows,
            patient_name, llm, language
        )
        
        return RiskSummaryOutput(
            overall_risk=overall_risk,
            summary=summary,
        )
    except Exception as e:
        logger.error(f"Error in LLM summarization: {str(e)}") 
        return _create_fallback_summary(
            overall_risk, high_risk, medium_risk, low_risk,
            high_risk_flows, medium_risk_flows, low_risk_flows,
            language
        )


# ------------------------------------------------------------
# Patient Question Answering
# ------------------------------------------------------------

def answer_patient_questions(
    question: str, 
    patient_context: dict, 
    llm,
    risk_results: Dict[str, Dict[str, str]] = None,
    procedures: str = None,
    language: str = 'th'
) -> PatientQuestionAnswer:
    """ตอบคำถามผู้ป่วยด้วย LLM"""
    
    if not question or question.strip() == "":
        return PatientQuestionAnswer(
            answer="ไม่มีคำถามเพิ่มเติม",
            urgency_level="ปกติ",
            should_contact_doctor=False,
            related_risks=[]
        )
    
    # สร้างบริบทผู้ป่วย
    context_parts = []
    if patient_context:
        if 'age' in patient_context:
            context_parts.append(f"อายุ {patient_context['age']} ปี")
        if 'gender' in patient_context:
            context_parts.append(f"เพศ {patient_context['gender']}")
        if 'surgery_date' in patient_context:
            context_parts.append(f"ผ่าตัดเมื่อ: {patient_context['surgery_date']}")
    
    # แปลง procedures
    if procedures and procedures != 'ไม่ระบุ':
        if isinstance(procedures, list):
            proc_list = [str(p) for p in procedures if p]
            if proc_list:
                context_parts.append(f"หัตถการ: {', '.join(proc_list)}")
                proc_str = ', '.join(proc_list)
        else:
            context_parts.append(f"หัตถการ: {procedures}")
            proc_str = str(procedures)
    else:
        proc_str = None
    
    context_str = ", ".join(context_parts) if context_parts else None
    
    # เพิ่มบริบทจากผลการประเมินความเสี่ยง
    risk_context = ""
    if risk_results:
        high_risks = []
        medium_risks = []
        for flow_name, result in risk_results.items():
            if 'สูง' in result.get('risk_level', ''):
                high_risks.append(f"{flow_name}: {result.get('reason', '')}")
            elif 'กลาง' in result.get('risk_level', '') or 'ปานกลาง' in result.get('risk_level', ''):
                medium_risks.append(f"{flow_name}: {result.get('reason', '')}")
        
        if high_risks or medium_risks:
            risk_context = "\n\nผลการประเมินความเสี่ยง:\n"
            if high_risks:
                risk_context += "ความเสี่ยงสูง:\n" + "\n".join(f"- {r}" for r in high_risks) + "\n"
            if medium_risks:
                risk_context += "ความเสี่ยงปานกลาง:\n" + "\n".join(f"- {r}" for r in medium_risks[:3])
    
    # สร้าง role
    role = "คุณเป็นพยาบาลหญิงผู้เชี่ยวชาญด้านการดูแลผู้ป่วย"
    if proc_str:
        role += f"หลัง{proc_str}"
    
    parser = PydanticOutputParser(pydantic_object=PatientQuestionAnswer)
    format_instructions = parser.get_format_instructions()
    
    prompt = build_patient_question_prompt(
        question=question,
        context_str=context_str,
        risk_context=risk_context,
        proc_str=proc_str,
        format_instructions=format_instructions,
        language=language
    )
    
    print("\n" + "="*80)
    print("📝 PROMPT: answer_patient_questions")
    print("="*80)
    print(prompt)
    print("="*80 + "\n")
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        result = parser.parse(content)
        return result
    except Exception as e:
        print(f"Error in answer_patient_questions: {str(e)}")
        return PatientQuestionAnswer(
            answer="ขออภัย ไม่สามารถตอบคำถามได้ในขณะนี้ กรุณาติดต่อทีมแพทย์โดยตรง",
            urgency_level="เร่งด่วน",
            should_contact_doctor=True,
            related_risks=["ไม่สามารถวิเคราะห์ได้"]
        )
