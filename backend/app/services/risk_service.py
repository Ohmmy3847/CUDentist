from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
import asyncio
from typing import List, Dict, Any

from app.core.constants import (
    FIELD_LABELS,
    FORM_COLUMNS,
    PHONE_NUMBER
)
from app.services.flow_parser import RuleEngine
from app.services.prompts import (
    build_high_risk_prompt,
    build_medium_risk_prompt,
    build_patient_question_prompt,
)



class RiskSummaryContent(BaseModel):
    """Pydantic model for LLM risk summary output (due-to clause only)"""
    risk_summary: str = Field(description="Short phrase summarizing risk reasons (clause after due to / เนื่องจาก)")


def build_llm(api_key: str, model_name: str = "deepseek-chat"):
    """Build DeepSeek LLM for text analysis"""
    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url="https://api.deepseek.com",
        temperature=0.1,
        max_tokens=5000
    )

# ── ชื่อ Topic สำหรับแสดงในข้อความ ─────────────────────────────────────────
# key = flow_name จริงๆ ที่ RuleEngine ส่งมา (ดูจาก evaluators dict ใน flow_parser.py)
# แก้ค่า 'th' / 'en' เพื่อเปลี่ยนชื่อที่แสดง
FLOW_TOPIC_NAMES: dict[str, dict[str, str]] = {
    # ── Flow ปกติ ──────────────────────────────────────────────────────────
    'pain':                 {'th': 'อาการปวด',      'en': 'Pain'},
    'swelling':             {'th': 'อาการบวม',      'en': 'Swelling'},
    'bleeding':             {'th': 'เลือดออก',      'en': 'Bleeding'},
    'fever':                {'th': 'ไข้',           'en': 'Fever'},
    'numbness':             {'th': 'อาการชา',       'en': 'Numbness'},
    'phlebitis':            {'th': 'บริเวณที่เอาเข็มน้ำเกลือออกที่หลังมือหรือข้อมือ',   'en': 'phlebitis at needle site'},
    'suture':               {'th': 'ไหมเย็บแผล',    'en': 'Suture'},
    'other_symptoms':       {'th': 'อาการอื่นๆ',    'en': 'Other Symptoms'},
    'antibiotics_compliance': {'th': 'ยาฆ่าเชื้อ',    'en': 'Antibiotics'},
    'compress':             {'th': 'การประคบ',      'en': 'Compress'},
    'imf_wire':             {'th': 'ลวดมัดฟัน',     'en': 'IMF Wire'},
    'walking':              {'th': 'การเดิน',       'en': 'Walking'},
    'ng_tube':              {'th': 'สายให้อาหาร',   'en': 'NG Tube'},
    'brushing':             {'th': 'การแปรงฟัน',    'en': 'Brushing'},
    'rinsing':              {'th': 'การบ้วนปาก',    'en': 'Rinsing'},
    'food_type':            {'th': 'ประเภทอาหาร',   'en': 'Food Type'},
    'food_intake':          {'th': 'ปริมาณอาหาร',   'en': 'Food Intake'},
    
    # ── อาการอื่นๆ (key = symptom key จาก symptom_map ใน flow_parser.py) ──
    'sinus_pain':       {'th': 'ปวดหน้าแก้ม',     'en': 'Sinus Pain'},
    'nausea_vomiting':  {'th': 'คลื่นไส้/อาเจียน', 'en': 'Nausea/Vomiting'},
    'cough':            {'th': 'ไอ/เสมหะ',         'en': 'Cough'},
    'stuffy_nose':      {'th': 'คัดจมูก',           'en': 'Stuffy Nose'},
    'bruising':         {'th': 'รอยช้ำ',            'en': 'Bruising'},
    'diarrhea':         {'th': 'ท้องเสีย',          'en': 'Diarrhea'},
    'runny_nose':       {'th': 'น้ำมูก',            'en': 'Runny Nose'},
    'sore_throat':      {'th': 'เจ็บคอ',            'en': 'Sore Throat'},
    'weight_loss':      {'th': 'น้ำหนักลด',         'en': 'Weight Loss'},
    'headache':         {'th': 'ปวดหัว',            'en': 'Headache'},
}
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────

RISK_TRANSLATIONS = {
    'th': {
        'High': 'ความเสี่ยงสูง',
        'Medium': 'ความเสี่ยงปานกลาง',
        'Low': 'ความเสี่ยงต่ำ',
        'Complicated': 'ซับซ้อน'
    },
    'en': {
        'High': 'High',
        'Medium': 'Medium',
        'Low': 'Low',
        'Complicated': 'Complicated'
    }
}
# ------------------------------------------------------------
# Pydantic Models
# ------------------------------------------------------------
class OutputRiskClassification(BaseModel):
    risk_level: str = Field(description="ระดับความเสี่ยงของผู้ป่วย [ความเสี่ยงต่ำ, ความเสี่ยงกลาง, ความเสี่ยงสูง]")
    recommendation: str = Field(description="คำแนะนำการดูแลตนเองสำหรับผู้ป่วย เขียนเป็นภาษาไทย ต้องบอกชัดว่าควรทำอะไร")
    reason: str = Field(description="เหตุผลที่ประเมินระดับความเสี่ยงนี้ เขียนเป็นภาษาไทย")


class RiskSummaryOutput(BaseModel):
    """Output model สำหรับ summarize_all_risks"""
    overall_risk: str = Field(description="ระดับความเสี่ยงโดยรวม")
    summary: str = Field(description="สรุปผลการประเมินสำหรับผู้ป่วย")
    critical_issues: List[str] = Field(default_factory=list, description="รายการปัญหาวิกฤติ")


class PatientQuestionAnswer(BaseModel):
    """Output model สำหรับ answer_patient_questions"""
    answer: str = Field(description="คำตอบสำหรับผู้ป่วย")
    urgency_level: str = Field(description="ระดับความเร่งด่วน: ปกติ, ควรติดตาม, เร่งด่วน")
    should_contact_doctor: bool = Field(description="ควรติดต่อแพทย์หรือไม่")
    related_risks: List[str] = Field(default_factory=list, description="ความเสี่ยงที่เกี่ยวข้อง")


# ------------------------------------------------------------
# Helper Functions for Risk Summarization
# ------------------------------------------------------------

def _categorize_risks_by_level(all_results: Dict[str, Dict[str, str]], language: str = 'th') -> tuple:
    """
    แยก results ตามระดับความเสี่ยง
    
    Returns:
        tuple: (high_risk, high_risk_flows, medium_risk, medium_risk_flows, low_risk, low_risk_flows, complicated_risk, complicated_risk_flows)
    """
    high_risk = []
    high_risk_flows = []
    medium_risk = []
    medium_risk_flows = []
    low_risk = []
    low_risk_flows = []
    complicated_risk = []
    complicated_risk_flows = []
    
    for flow_name, result in all_results.items():
        risk_level = result['risk_level']
        display_name = _normalize_topic(flow_name, language)  # ← normalize ก่อนใช้
        
        # จัดการ other_symptoms ที่คืนค่าเป็น list
        if 'reasons' in result and 'recommendations' in result:
            # other_symptoms: มี reasons (list) และ recommendations (list)
            reasons_text = ', '.join(result['reasons'])
            if 'สูง' in risk_level:
                high_risk.append(f"{display_name}: {reasons_text}")
                high_risk_flows.append((flow_name, result))
            elif 'กลาง' in risk_level or 'ปานกลาง' in risk_level:
                medium_risk.append(f"{display_name}: {reasons_text}")
                medium_risk_flows.append((flow_name, result))
            elif 'ซับซ้อน' in risk_level or 'ไม่สามารถสรุป' in risk_level:
                complicated_risk.append(f"{display_name}: {reasons_text}")
                complicated_risk_flows.append((flow_name, result))
            elif 'ต่ำ' in risk_level:
                low_risk.append(f"{display_name}: {reasons_text}")
                low_risk_flows.append((flow_name, result))
        else:
            # flow ปกติ: มี reason (string)
            if 'สูง' in risk_level:
                high_risk.append(f"{display_name}: {result['reason']}")
                high_risk_flows.append((flow_name, result))
            elif 'กลาง' in risk_level or 'ปานกลาง' in risk_level:
                medium_risk.append(f"{display_name}: {result['reason']}")
                medium_risk_flows.append((flow_name, result))
            elif 'ซับซ้อน' in risk_level or 'ไม่สามารถสรุป' in risk_level:
                complicated_risk.append(f"{display_name}: {result['reason']}")
                complicated_risk_flows.append((flow_name, result))
            elif 'ต่ำ' in risk_level:
                low_risk.append(f"{display_name}: {result['reason']}")
                low_risk_flows.append((flow_name, result))
    
    return high_risk, high_risk_flows, medium_risk, medium_risk_flows, low_risk, low_risk_flows, complicated_risk, complicated_risk_flows


def _calculate_overall_risk(high_risk_count: int, medium_risk_count: int, complicated_risk_count: int) -> str:
    """
    คำนวณระดับความเสี่ยงโดยรวมด้วย rule-based logic
    
    ลำดับความสำคัญ: สูง > กลาง > ซับซ้อน > ต่ำ
    
    หมายเหตุ:
    - "ซับซ้อน" (COMPLICATED) = ผู้ป่วยระบุอาการอื่นๆที่ไม่มีในตัวเลือก (other_symptoms_custom)
      ในคำถาม "อาการอื่นๆ (เลือกได้หลายคำตอบ)"
    
    Args:
        high_risk_count: จำนวนความเสี่ยงสูง
        medium_risk_count: จำนวนความเสี่ยงปานกลาง
        complicated_risk_count: จำนวนอาการซับซ้อน (ระบุอาการที่ไม่อยู่ในตัวเลือก)
    
    Returns:
        str: ระดับความเสี่ยงโดยรวม (English Key: High, Medium, Low, Complicated)
    """
    # เช็คตามลำดับความสำคัญ: สูง > กลาง > ซับซ้อน > ต่ำ
    if high_risk_count >= 1:
        return 'High'
    elif medium_risk_count >= 1:
        return 'Medium'
    elif complicated_risk_count >= 1:
        return 'Complicated'
    else:
        return 'Low'


def _build_critical_issues(high_risk_flows: List[tuple], language: str = 'th') -> List[str]:
    """
    สร้างรายการปัญหาวิกฤติจากความเสี่ยงสูง
    
    Args:
        high_risk_flows: List of (flow_name, result) tuples
        language: 'th' หรือ 'en'
    
    Returns:
        List[str]: รายการปัญหาวิกฤติ
    """
    critical_issues = []
    for flow_name, result in high_risk_flows:
        topic = _normalize_topic(flow_name, language)
        critical_issues.append(f"⚠️ {topic}: {result['reason']}")
    return critical_issues


def _normalize_topic(topic: str, language: str = 'th') -> str:
    """
    แปลง flow_name → ชื่อ topic ที่แสดงในข้อความ
    1. ถ้ามีใน FLOW_TOPIC_NAMES → ใช้ชื่อที่กำหนดไว้
    2. ถ้าไม่มี → fallback: แทน underscore ด้วย space + Title Case
    """
    entry = FLOW_TOPIC_NAMES.get(topic)
    if entry:
        return entry.get(language, entry.get('th', topic))
    return topic.replace('_', ' ').strip().title()



def _extract_recommendations_from_flows(flows: List[tuple], language: str = 'th') -> List[tuple]:
    """
    ดึง (topic, rec) จาก flow results โดยตรง — rule-based 100%
    
    Args:
        flows: List of (flow_name, result) tuples
        language: 'th' หรือ 'en'
    
    Returns:
        List of (topic, rec) tuples
    """
    items = []
    for flow_name, result in flows:
        # ข้าม COMPLICATED (อาการที่ผู้ป่วยระบุเพิ่มเติม) — ไม่ต้องแสดงคำแนะนำ
        if 'ซับซ้อน' in result.get('risk_level', '') or 'complicated' in result.get('risk_level', '').lower():
            continue

        # flow ปกติ: recommendation เป็น string (ไม่มี 'recommendations' list)
        if 'recommendations' in result and isinstance(result['recommendations'], list):
            # กรณี other_symptoms batch (legacy) — ไม่ควรเกิดแล้วแต่ fallback ไว้
            reasons = result.get('reasons', [])
            recs = result['recommendations']
            for i, rec in enumerate(recs):
                if rec:
                    topic_key = reasons[i] if i < len(reasons) else flow_name
                    items.append((_normalize_topic(topic_key, language), rec))
        else:
            rec = result.get('recommendation', '')
            if rec:
                # อาการอื่นๆ: ใช้ symptom_key lookup จาก FLOW_TOPIC_NAMES
                symptom_key = result.get('symptom_key')
                if symptom_key:
                    topic = _normalize_topic(symptom_key, language)
                else:
                    topic = _normalize_topic(flow_name, language)
                items.append((topic, rec))
    return items


def _format_high_risk_message(
    risk_summary: str,
    high_recs: List[tuple],
    other_recs: List[tuple],
    name_text: str,
    language: str = 'th'
) -> str:
    """จัด format ข้อความสำหรับกรณีเสี่ยงสูง — Python control ทุก format"""
    lines = []
    if language == 'en':
        if not risk_summary.strip().endswith('.'):
            risk_summary = risk_summary.strip() + "."
        lines.append(f"Based on your symptoms, {name_text} has a HIGH risk of complications.")
        lines.append(f"Due to {risk_summary}")
        if high_recs:
            lines.append("\nRecommendation:")
            for topic, rec in high_recs:
                lines.append(f"• {topic}: {rec}")
        lines.append(f"\nPlease call a nurse now at {PHONE_NUMBER} for a check-up or special visit.")
        if other_recs:
            lines.append("\nMore advices based on symptoms:")
            for topic, rec in other_recs:
                lines.append(f"• {topic}: {rec}")
    else:
        lines.append(f"จากการประเมิน พบว่า{name_text} มีความเสี่ยงต่อการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปากในระดับสูง")
        lines.append(f"เนื่องจาก {risk_summary}")
        if high_recs:
            lines.append("\nแนะนำ:")
            for topic, rec in high_recs:
                lines.append(f"• {topic}: {rec}")
        lines.append(f"\nแนะนำให้ติดต่อพยาบาลโดยเร็ว โทร {PHONE_NUMBER} เพื่อรับการประเมินอาการหรือนัดหมายเป็นกรณีพิเศษ")
        if other_recs:
            lines.append("\nคำแนะนำเพิ่มเติมตามอาการ")
            for topic, rec in other_recs:
                lines.append(f"• {topic}: {rec}")
    return "\n".join(lines)


def _format_medium_risk_message(
    risk_summary: str,
    medium_recs: List[tuple],
    other_recs: List[tuple],
    name_text: str,
    language: str = 'th'
) -> str:
    """จัด format ข้อความสำหรับกรณีเสี่ยงปานกลาง — Python control ทุก format"""
    lines = []
    if language == 'en':
        if not risk_summary.strip().endswith('.'):
            risk_summary = risk_summary.strip() + "."
        lines.append(f"Based on your symptoms, {name_text} has a MODERATE risk of complications.")
        lines.append(f"Due to {risk_summary}")
        if medium_recs:
            lines.append("\nRecommendation:")
            for topic, rec in medium_recs:
                lines.append(f"• {topic}: {rec}")
        lines.append(f"\nThe nursing team will call you for a check-up. If you have any questions, call {PHONE_NUMBER}.")
        if other_recs:
            lines.append("\nMore advices based on symptoms:")
            for topic, rec in other_recs:
                lines.append(f"• {topic}: {rec}")
    else:
        lines.append(f"จากการประเมิน พบว่า{name_text} มีความเสี่ยงต่อการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปากระดับปานกลาง")
        lines.append(f"เนื่องจาก {risk_summary}")
        if medium_recs:
            lines.append("\nแนะนำ:")
            for topic, rec in medium_recs:
                lines.append(f"• {topic}: {rec}")
        lines.append(f"\nทีมพยาบาลจะติดต่อกลับเพื่อประเมินอาการเพิ่มเติม สอบถามเพิ่มเติม โทร {PHONE_NUMBER}")
        if other_recs:
            lines.append("\nคำแนะนำเพิ่มเติมตามอาการ")
            for topic, rec in other_recs:
                lines.append(f"• {topic}: {rec}")
    return "\n".join(lines)


def _format_low_risk_message(
    risk_summary: str,
    all_recs: List[tuple],
    name_text: str,
    language: str = 'th'
) -> str:
    """จัด format ข้อความสำหรับกรณีเสี่ยงต่ำ — Python control ทุก format"""
    lines = []
    if language == 'en':
        if not risk_summary.strip().endswith('.'):
            risk_summary = risk_summary.strip() + "."
        lines.append("Based on the assessment, the risk of complications is LOW.")
        lines.append(f"Overall symptoms are within normal range.")
        if all_recs:
            lines.append("\nAdvices based on your symptoms:")
            for topic, rec in all_recs:
                lines.append(f"• {topic}: {rec}")
        lines.append(f"\nIf you have questions, call {PHONE_NUMBER}")
    else:
        lines.append("จากผลประเมินพบว่ามีความเสี่ยงในการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปาก ระดับต่ำ")
        lines.append(f"อาการโดยรวมอยู่ในเกณฑ์ปกติ")
        if all_recs:
            lines.append("\nคำแนะนำเบื้องต้นตามอาการ")
            for topic, rec in all_recs:
                lines.append(f"• {topic}: {rec}")
        lines.append(f"\nหากมีข้อสงสัย โทร {PHONE_NUMBER}")
    return "\n".join(lines)


def _format_complex_case_message(
    risk_summary: str,
    all_recs: List[tuple],
    language: str = 'th'
) -> str:
    """จัด format ข้อความสำหรับกรณีซับซ้อน — Python control ทุก format"""
    lines = []
    if language == 'en':
        lines.append("Based on your symptoms, the risk level cannot be determined due to complex symptoms.")
        lines.append(f"The nurse team will call you for a check-up. If you have questions, call {PHONE_NUMBER}.")
        if all_recs:
            lines.append("\nAdvices based on your symptoms:")
            for topic, rec in all_recs:
                lines.append(f"• {topic}: {rec}")
    else:
        lines.append("จากการประเมินความเสี่ยงในการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปาก พบว่าไม่สามารถสรุปผลความเสี่ยงได้เนื่องจากอาการมีความซับซ้อน")
        lines.append(f"ทีมพยาบาลจะติดต่อกลับเพื่อประเมินอาการเพิ่มเติม หากมีข้อสงสัย โทร {PHONE_NUMBER}")
        if all_recs:
            lines.append("\nคำแนะนำเบื้องต้นตามอาการ")
            for topic, rec in all_recs:
                lines.append(f"• {topic}: {rec}")
    return "\n".join(lines)



def _extract_json_from_response(text: str) -> str:
    """
    ดึง JSON จาก LLM response ที่อาจ wrap ด้วย markdown code block
    DeepSeek มักจะ return ```json ... ``` ซึ่ง PydanticOutputParser parse ไม่ได้
    """
    import re
    # ลอง strip markdown code block ก่อน
    match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if match:
        return match.group(1).strip()
    # ถ้าไม่มี code block ให้ return ตรงๆ
    return text.strip()


def _parse_llm_json(parser, response_text: str):
    """Parse LLM response โดย handle markdown code block ด้วย"""
    clean_text = _extract_json_from_response(response_text)
    try:
        return parser.parse(clean_text)
    except Exception:
        # fallback: ลอง parse ตรงๆ อีกครั้ง
        return parser.parse(response_text)


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
    high_recs = _extract_recommendations_from_flows(high_risk_flows, language)
    medium_recs = _extract_recommendations_from_flows(medium_risk_flows, language)
    low_recs = _extract_recommendations_from_flows(low_risk_flows, language)

    try:
        # LLM ทำแค่ risk_summary
        parser = PydanticOutputParser(pydantic_object=RiskSummaryContent)

        if overall_risk == 'High':
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
            content = _parse_llm_json(parser, response.content)
            return _format_high_risk_message(content.risk_summary, high_recs, other_recs, name_text, language)

        elif overall_risk == 'Medium':
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
            content = _parse_llm_json(parser, response.content)
            return _format_medium_risk_message(content.risk_summary, medium_recs, other_recs, name_text, language)

        elif overall_risk == 'Low':
            # Should not happen via optimization, but handle just in case
            return _format_low_risk_message(
                 risk_summary="ไม่พบความเสี่ยงที่มีนัยสำคัญ" if language == 'th' else "No significant risks found.",
                 all_recs=low_recs,
                 name_text=name_text,
                 language=language
            )

    except Exception as e:
        print(f"Error generating patient summary: {e}")
        
        # Determine appropriate recs for fallback
        fallback_recs = []
        fallback_reasons = []
        if overall_risk == 'High':
            fallback_recs = high_recs + medium_recs + low_recs
            fallback_reasons = high_risk
        elif overall_risk == 'Medium':
            fallback_recs = medium_recs + low_recs
            fallback_reasons = medium_risk
        elif overall_risk == 'Low':
            fallback_recs = low_recs
            fallback_reasons = []
            
        return _generate_fallback_summary_text(
            overall_risk=overall_risk,
            name_text=name_text,
            language=language,
            reasons=fallback_reasons,
            all_recs=fallback_recs
        )



def _generate_fallback_summary_text(
    overall_risk: str, 
    name_text: str, 
    language: str = 'th',
    reasons: List[str] = None,
    all_recs: List[tuple] = None
) -> str:
    """สร้าง fallback text เมื่อ LLM error — แสดง rule-based reasons"""
    lines = []
    
    if language == 'en':
        if overall_risk == 'High':
            lines.append(f"Based on your symptoms, {name_text if name_text else 'the patient'} has a HIGH risk of complications.")
            if reasons:
                lines.append("Reasons: " + ", ".join(reasons) + ".")
            lines.append(f"\nPlease call a nurse now at {PHONE_NUMBER} for a check-up or special visit.")
        elif overall_risk == 'Medium':
            lines.append(f"Based on your symptoms, {name_text if name_text else 'the patient'} has a MODERATE risk of complications.")
            if reasons:
                lines.append("Reasons: " + ", ".join(reasons) + ".")
            lines.append(f"\nThe nursing team will call you for a check-up. If you have any questions, call {PHONE_NUMBER}.")
        else:
            lines.append("Based on the assessment, the risk of complications is LOW.")
            lines.append("Overall symptoms are within normal range.")
            lines.append(f"\nIf you have questions, call {PHONE_NUMBER}")

    else: # Thai fallback
        if overall_risk == 'High':
            lines.append(f"จากการประเมิน พบว่า{name_text}มีความเสี่ยงต่อการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปากในระดับสูง")
            if reasons:
                lines.append("เนื่องจาก: " + ", ".join(reasons))
            lines.append(f"\nแนะนำให้โทรติดต่อพยาบาลทันที โทร {PHONE_NUMBER} เพื่อนัดตรวจหรือนัดพิเศษ")
        elif overall_risk == 'Medium':
            lines.append(f"จากการประเมิน พบว่า{name_text}มีความเสี่ยงต่อการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปากระดับปานกลาง")
            if reasons:
                lines.append("เนื่องจาก: " + ", ".join(reasons))
            lines.append(f"\nทีมพยาบาลจะติดต่อกลับเพื่อประเมินอาการเพิ่มเติม สอบถามเพิ่มเติม โทร {PHONE_NUMBER}")
        else:
            lines.append("จากผลประเมินพบว่ามีความเสี่ยงในการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปาก ระดับต่ำ")
            lines.append("อาการโดยรวมอยู่ในเกณฑ์ปกติ")
            lines.append(f"\nหากมีข้อสงสัย โทร {PHONE_NUMBER}")
            
    # Append recommendations if available
    if all_recs:
        header = "\nAdvices based on symptoms:" if language == 'en' else "\nคำแนะนำเพิ่มเติมตามอาการ:"
        lines.append(header)
        for topic, rec in all_recs:
            lines.append(f"• {topic}: {rec}")
            
    return "\n".join(lines)


# Note: _generate_summary_prompt function was removed as it's no longer used.
# The system now uses _generate_patient_summary instead.


def _create_fallback_summary(
    overall_risk: str,
    high_risk: List[str],
    medium_risk: List[str],
    low_risk: List[str],
    high_risk_flows: List[tuple],
    medium_risk_flows: List[tuple],
    low_risk_flows: List[tuple],
    critical_issues: List[str],
    language: str = 'th'
) -> RiskSummaryOutput:
    """
    สร้าง fallback summary เมื่อ LLM ไม่พร้อมใช้งาน
    
    Returns:
        RiskSummaryOutput: Summary object แบบ simple
    """
    
    # Summary for patient (with recommendations merged)
    patient_summary_parts = []
    if high_risk:
        patient_summary_parts.append(f"พบความเสี่ยงสูง {len(high_risk)} รายการ ต้องดูแลอย่างใกล้ชิด")
    if medium_risk:
        patient_summary_parts.append(f"มีความเสี่ยงปานกลาง {len(medium_risk)} รายการ")
    
    # Add recommendations to patient summary
    rec_parts = []
    
    # Collect recommendations from ALL levels for fallback
    for flow_name, result in high_risk_flows:
        if result['recommendation']:
            rec_parts.append(result['recommendation'])
    for flow_name, result in medium_risk_flows:
        if result['recommendation']:
            rec_parts.append(result['recommendation'])
    # Also include low risk recommendations in fallback (important!)
    for flow_name, result in low_risk_flows:
         if result['recommendation']:
             rec_parts.append(result['recommendation'])

    if patient_summary_parts:
        summary = " ".join(patient_summary_parts)
        if rec_parts:
            summary += (" Recommendation: " if language == 'en' else " คำแนะนำ: ") + " ".join(rec_parts[:3])  # Top 3 recommendations
    else:
        # If no risk parts (Low risk), show generic message + recommendations
        base_msg = "Symptoms are normal." if language == 'en' else "อาการอยู่ในเกณฑ์ปกติ"
        if rec_parts:
             recs_str = " ".join(rec_parts[:3]) # Show simplified recs
             summary = f"{base_msg} {recs_str}"
        else:
             summary = "Symptoms are normal. Follow doctor's advice." if language == 'en' else "อาการอยู่ในเกณฑ์ปกติ ดูแลตามคำแนะนำจากแพทย์"
    
    # Get localized risk level
    translation_map = RISK_TRANSLATIONS.get(language, RISK_TRANSLATIONS['th'])
    localized_risk = translation_map.get(overall_risk, overall_risk)
    
    return RiskSummaryOutput(
        overall_risk=localized_risk,
        summary=summary,
        critical_issues=critical_issues
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
    
    Args:
        all_results: ผลการประเมินจากทุก flows {flow_name: {risk_level, reason, recommendation}}
        llm: LLM instance (ใช้สำหรับสรุป summary และ recommendations)
        patient_data: ข้อมูลผู้ป่วยเดิม (optional) - ควรมี 'name' field
        procedures: หัตถการที่ผู้ป่วยเข้ารับ (optional)
    
    Returns:
        RiskSummaryOutput object containing overall_risk, summary, recommendations, critical_issues
    """

    # 0. Translate flow names if language is English
    if language == 'en':
        translated_results = {}
        for flow_name, result in all_results.items():
            entry = FLOW_TOPIC_NAMES.get(flow_name)
            translated_name = entry['en'] if entry else flow_name
            translated_results[translated_name] = result
        all_results = translated_results
        
    translation_map = RISK_TRANSLATIONS.get(language, RISK_TRANSLATIONS['th'])

    # 1. แยกตามระดับควาวามเสี่ยง
    (high_risk, high_risk_flows, medium_risk, 
     medium_risk_flows, low_risk, low_risk_flows,
     complicated_risk, complicated_risk_flows) = _categorize_risks_by_level(all_results, language)
    
    # 2. คำนวณความเสี่ยงโดยรวม (Rule-based)
    overall_risk = _calculate_overall_risk(len(high_risk), len(medium_risk), len(complicated_risk))
    
    # 3. สร้าง Critical Issues
    critical_issues = _build_critical_issues(high_risk_flows, language)
    
    # 4. ดึงชื่อผู้ป่วย - รองรับทั้ง first_name+last_name และ name เก่า
    patient_name = ""
    if patient_data and isinstance(patient_data, dict):
        # Try first_name + last_name first (new format)
        first_name = patient_data.get('first_name', '')
        last_name = patient_data.get('last_name', '')
        if first_name or last_name:
            patient_name = f"{first_name}".strip()
    
    # 5. ถ้าไม่มี LLM ให้ใช้ fallback
    if not llm:
        return _create_fallback_summary(
            overall_risk, high_risk, medium_risk, low_risk,
            high_risk_flows, medium_risk_flows, low_risk_flows,
            critical_issues,
            language
        )
    
    # 6. Optimization: Skip LLM for Low and Complicated risks
    if overall_risk == 'Low' or overall_risk == 'Complicated':
        # Use static summary
        print(f"Skipping LLM for {overall_risk} risk")
        
        summary = ""
        if overall_risk == 'Low':
            low_recs = _extract_recommendations_from_flows(low_risk_flows, language)
            summary = _format_low_risk_message(
                risk_summary="ไม่พบความเสี่ยงที่มีนัยสำคัญ" if language == 'th' else "No significant risks found.",
                all_recs=low_recs,
                name_text=f"คุณ{patient_name}" if patient_name else "ผู้ป่วย",
                language=language
            )
        else: # Complicated แนะนำ low risk ได้
            low_recs = _extract_recommendations_from_flows(low_risk_flows, language)
            summary = _format_complex_case_message(
                risk_summary="", # Not used in complex case formatter
                all_recs=low_recs,
                language=language
            )
            
        return RiskSummaryOutput(
            overall_risk=translation_map.get(overall_risk, overall_risk),
            summary=summary,
            critical_issues=critical_issues
        )

    # 7. เรียก LLM สร้าง summary สำหรับผู้ป่วย (LLM ทำแค่ risk_summary, Python จัด rec)
    try:
        summary = _generate_patient_summary(
            overall_risk, high_risk, medium_risk,
            high_risk_flows, medium_risk_flows, low_risk_flows,
            patient_name, llm, language
        )
        
        return RiskSummaryOutput(
            overall_risk=translation_map.get(overall_risk, overall_risk),
            summary=summary,
            critical_issues=critical_issues
        )
    except Exception as e:
        logger.error(f"Error in LLM summarization: {str(e)}") 
        return _create_fallback_summary(
            overall_risk, high_risk, medium_risk, low_risk,
            high_risk_flows, medium_risk_flows, low_risk_flows,
            critical_issues,
            language
        )


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
    
    # 👇 เพิ่ม logging
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


# ------------------------------------------------------------
# Main Risk Classification Functions (Rule-Based)
# ------------------------------------------------------------
def classify_risk(input_data: dict, api_key: str = None, flow: str = None, flow_name: str = None, llm=None, max_retries: int = 3, language: str = 'th'):
    """
    Classify risk using Rule Engine (deterministic)
    Args:
        input_data: Patient data dictionary
        api_key: Google API key (optional, kept for backward compatibility)
        flow: Risk flow criteria (kept for backward compatibility, not used)
        flow_name: Name of the flow to evaluate
        llm: Pre-built LLM instance (optional, kept for backward compatibility)
        max_retries: Maximum number of retries (kept for backward compatibility)
        language: Language for output ('th' or 'en')
    """
    # Use Rule Engine for deterministic classification
    engine = RuleEngine()
    
    try:
        # Rule-based evaluation (deterministic)
        result = engine.evaluate_flow(flow_name, input_data, language=language)
        
        # Convert to OutputRiskClassification format
        return OutputRiskClassification(
            risk_level=result.get('risk_level', 'ไม่สามารถประเมินได้'),
            recommendation=result.get('recommendation'),
            reason=result.get('reason')
        )
        
    except Exception as e:
        print(f"Error in rule-based classification for {flow_name}: {str(e)}")
        
        # Fallback to default response
        return OutputRiskClassification(
            risk_level="ไม่สามารถประเมินได้" if language == 'th' else "Cannot assess",
            recommendation="กรุณาติดต่อทีมแพทย์เพื่อประเมินเพิ่มเติม" if language == 'th' else "Please contact medical team for further assessment",
            reason=f"ไม่สามารถประเมินได้: {str(e)[:100]}" if language == 'th' else f"Cannot assess: {str(e)[:100]}"
        )


# Async version for concurrent processing
async def classify_risk_async(input_data: dict, llm, flow: str, flow_name: str, semaphore, max_retries: int = 3, language: str = 'th'):
    """
    Classify risk using Rule Engine (deterministic, async wrapper)
    Note: This function uses async for API compatibility
    """
    async with semaphore:
        try:
            # Use Rule Engine for deterministic classification
            engine = RuleEngine()
            
            # Run in thread pool to maintain async compatibility
            loop = asyncio.get_event_loop()
            result_dict = await loop.run_in_executor(
                None,
                lambda: engine.evaluate_flow(flow_name, input_data, language=language)
            )
            
            # Convert to OutputRiskClassification format
            result = OutputRiskClassification(
                risk_level=result_dict.get('risk_level', 'ไม่สามารถประเมินได้'),
                recommendation=result_dict.get('recommendation'),
                reason=result_dict.get('reason')
            )
            
            return flow_name, result
            
        except Exception as e:
            print(f"Error in flow {flow_name}: {str(e)}")
            
            # Return default safe response
            default_response = OutputRiskClassification(
                risk_level="ไม่สามารถประเมินได้" if language == 'th' else "Cannot assess",
                recommendation="กรุณาติดต่อทีมแพทย์เพื่อประเมินเพิ่มเติม" if language == 'th' else "Please contact medical team for further assessment",
                reason=f"ไม่สามารถประเมินได้: {str(e)[:100]}" if language == 'th' else f"Cannot assess: {str(e)[:100]}"
            )
            return flow_name, default_response





