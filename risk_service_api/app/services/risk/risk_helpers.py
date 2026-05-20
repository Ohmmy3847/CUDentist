"""
Risk Assessment Helper Functions

Helper functions สำหรับจัดการ risk assessment results:
- จัดหมวดหมู่ตามระดับความเสี่ยง
- คำนวณ overall risk
- Normalize topic names
- ดึง recommendations จาก flows
- จัด format ข้อความสำหรับแต่ละระดับความเสี่ยง
"""
import re
import logging
from typing import List, Dict, Any

from app.core.constants import FLOW_TOPIC_NAMES, PHONE_NUMBER

logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# Risk Categorization
# ------------------------------------------------------------

def categorize_risks_by_level(all_results: Dict[str, Dict[str, str]], language: str = 'th') -> tuple:
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
        display_name = normalize_topic(flow_name, language)
        
        # จัดการ other_symptoms ที่คืนค่าเป็น list
        if 'reasons' in result and 'recommendations' in result:
            reasons_text = ', '.join(result['reasons'])
            if 'สูง' in risk_level or 'high' in risk_level.lower():
                high_risk.append(f"{display_name}: {reasons_text}")
                high_risk_flows.append((flow_name, result))
            elif 'กลาง' in risk_level or 'ปานกลาง' in risk_level or 'medium' in risk_level.lower():
                medium_risk.append(f"{display_name}: {reasons_text}")
                medium_risk_flows.append((flow_name, result))
            elif 'ซับซ้อน' in risk_level or 'ไม่สามารถสรุป' in risk_level or 'complicated' in risk_level.lower():
                complicated_risk.append(f"{display_name}: {reasons_text}")
                complicated_risk_flows.append((flow_name, result))
            elif 'ต่ำ' in risk_level or 'low' in risk_level.lower():
                low_risk.append(f"{display_name}: {reasons_text}")
                low_risk_flows.append((flow_name, result))
        else:
            if 'สูง' in risk_level or 'high' in risk_level.lower():
                high_risk.append(f"{display_name}: {result['reason']}")
                high_risk_flows.append((flow_name, result))
            elif 'กลาง' in risk_level or 'ปานกลาง' in risk_level or 'medium' in risk_level.lower():
                medium_risk.append(f"{display_name}: {result['reason']}")
                medium_risk_flows.append((flow_name, result))
            elif 'ซับซ้อน' in risk_level or 'ไม่สามารถสรุป' in risk_level or 'complicated' in risk_level.lower():
                complicated_risk.append(f"{display_name}: {result['reason']}")
                complicated_risk_flows.append((flow_name, result))
            elif 'ต่ำ' in risk_level or 'low' in risk_level.lower():
                low_risk.append(f"{display_name}: {result['reason']}")
                low_risk_flows.append((flow_name, result))
    
    return high_risk, high_risk_flows, medium_risk, medium_risk_flows, low_risk, low_risk_flows, complicated_risk, complicated_risk_flows


def calculate_overall_risk(high_risk_count: int, medium_risk_count: int, complicated_risk_count: int, language: str = 'th') -> str:
    """
    คำนวณระดับความเสี่ยงโดยรวมด้วย rule-based logic
    ลำดับความสำคัญ: สูง > กลาง > ซับซ้อน > ต่ำ
    Returns the display string directly in the given language.
    """
    if language == 'en':
        if high_risk_count >= 1:
            return 'High Risk'
        elif medium_risk_count >= 1:
            return 'Medium Risk'
        elif complicated_risk_count >= 1:
            return 'Complicated'
        else:
            return 'Low Risk'
    else:
        if high_risk_count >= 1:
            return 'ความเสี่ยงสูง'
        elif medium_risk_count >= 1:
            return 'ความเสี่ยงปานกลาง'
        elif complicated_risk_count >= 1:
            return 'ซับซ้อน'
        else:
            return 'ความเสี่ยงต่ำ'


# ------------------------------------------------------------
# Topic Normalization
# ------------------------------------------------------------

def normalize_topic(topic: str, language: str = 'th') -> str:
    """
    แปลง flow_name → ชื่อ topic ที่แสดงในข้อความ
    1. ลบ prefix 'custom_symptom:'
    2. ถ้ามีใน FLOW_TOPIC_NAMES → ใช้ชื่อที่กำหนดไว้
    3. ถ้าไม่มี → fallback: แทน underscore ด้วย space + Title Case
    """
    if topic.startswith('custom_symptom:'):
        topic = topic.replace('custom_symptom:', '', 1)

    entry = FLOW_TOPIC_NAMES.get(topic)
    if entry:
        return entry.get(language, entry.get('th', topic))
    return topic.replace('_', ' ').strip().title()


# ------------------------------------------------------------
# Recommendation Extraction
# ------------------------------------------------------------

def extract_recommendations_from_flows(flows: List[tuple], language: str = 'th') -> List[tuple]:
    """
    ดึง (topic, rec) จาก flow results โดยตรง — rule-based 100%
    """
    items = []
    for flow_name, result in flows:
        if 'ซับซ้อน' in result.get('risk_level', '') or 'complicated' in result.get('risk_level', '').lower():
            continue

        if 'recommendations' in result and isinstance(result['recommendations'], list):
            reasons = result.get('reasons', [])
            recs = result['recommendations']
            for i, rec in enumerate(recs):
                if rec:
                    topic_key = reasons[i] if i < len(reasons) else flow_name
                    items.append((normalize_topic(topic_key, language), rec))
        else:
            rec = result.get('recommendation', '')
            if rec:
                symptom_key = result.get('symptom_key')
                if symptom_key:
                    topic = normalize_topic(symptom_key, language)
                else:
                    topic = normalize_topic(flow_name, language)
                items.append((topic, rec))
    return items


# ------------------------------------------------------------
# Message Formatting
# ------------------------------------------------------------

def format_high_risk_message(
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


def format_medium_risk_message(
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


def format_low_risk_message(
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


def format_complex_case_message(
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


# ------------------------------------------------------------
# LLM Response Parsing
# ------------------------------------------------------------

def extract_json_from_response(text: str) -> str:
    """
    ดึง JSON จาก LLM response ที่อาจ wrap ด้วย markdown code block
    DeepSeek มักจะ return ```json ... ``` ซึ่ง PydanticOutputParser parse ไม่ได้
    """
    match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if match:
        return match.group(1).strip()
    return text.strip()


def parse_llm_json(parser, response_text: str):
    """Parse LLM response โดย handle markdown code block ด้วย"""
    clean_text = extract_json_from_response(response_text)
    try:
        return parser.parse(clean_text)
    except Exception:
        return parser.parse(response_text)


def generate_fallback_summary_text(
    overall_risk: str, 
    name_text: str, 
    language: str = 'th',
    reasons: List[str] = None,
    all_recs: List[tuple] = None
) -> str:
    """สร้าง fallback text เมื่อ LLM error — แสดง rule-based reasons"""
    lines = []
    
    _high = {'High Risk', 'ความเสี่ยงสูง'}
    _medium = {'Medium Risk', 'ความเสี่ยงปานกลาง'}

    if language == 'en':
        if overall_risk in _high:
            lines.append(f"Based on your symptoms, {name_text if name_text else 'the patient'} has a HIGH risk of complications.")
            if reasons:
                lines.append("Reasons: " + ", ".join(reasons) + ".")
            lines.append(f"\nPlease call a nurse now at {PHONE_NUMBER} for a check-up or special visit.")
        elif overall_risk in _medium:
            lines.append(f"Based on your symptoms, {name_text if name_text else 'the patient'} has a MODERATE risk of complications.")
            if reasons:
                lines.append("Reasons: " + ", ".join(reasons) + ".")
            lines.append(f"\nThe nursing team will call you for a check-up. If you have any questions, call {PHONE_NUMBER}.")
        else:
            lines.append("Based on the assessment, the risk of complications is LOW.")
            lines.append("Overall symptoms are within normal range.")
            lines.append(f"\nIf you have questions, call {PHONE_NUMBER}")
    else:
        if overall_risk in _high:
            lines.append(f"จากการประเมิน พบว่า{name_text}มีความเสี่ยงต่อการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปากในระดับสูง")
            if reasons:
                lines.append("เนื่องจาก: " + ", ".join(reasons))
            lines.append(f"\nแนะนำให้โทรติดต่อพยาบาลทันที โทร {PHONE_NUMBER} เพื่อนัดตรวจหรือนัดพิเศษ")
        elif overall_risk in _medium:
            lines.append(f"จากการประเมิน พบว่า{name_text}มีความเสี่ยงต่อการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปากระดับปานกลาง")
            if reasons:
                lines.append("เนื่องจาก: " + ", ".join(reasons))
            lines.append(f"\nทีมพยาบาลจะติดต่อกลับเพื่อประเมินอาการเพิ่มเติม สอบถามเพิ่มเติม โทร {PHONE_NUMBER}")
        else:
            lines.append("จากผลประเมินพบว่ามีความเสี่ยงในการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปาก ระดับต่ำ")
            lines.append("อาการโดยรวมอยู่ในเกณฑ์ปกติ")
            lines.append(f"\nหากมีข้อสงสัย โทร {PHONE_NUMBER}")
            
    if all_recs:
        header = "\nAdvices based on symptoms:" if language == 'en' else "\nคำแนะนำเพิ่มเติมตามอาการ:"
        lines.append(header)
        for topic, rec in all_recs:
            lines.append(f"• {topic}: {rec}")
            
    return "\n".join(lines)
