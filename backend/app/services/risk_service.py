from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
import asyncio
from typing import List, Dict, Any

from app.core.flows import FLOWS
from app.core.constants import (
    FIELD_LABELS,
    FORM_COLUMNS,
    FIELD_WITH_DESCRIPTION,
    DESCRIPTION_LABELS,
    CUSTOM_TEXT_FIELDS,
    PHONE_NUMBER
)
from app.services.flow_parser import RuleEngine


# ------------------------------------------------------------
# Pydantic Models
# ------------------------------------------------------------
class OutputRiskClassification(BaseModel):
    risk_level: str = Field(description="ระดับความเสี่ยงของผู้ป่วย [ความเสี่ยงต่ำ, ความเสี่ยงกลาง, ความเสี่ยงสูง]")
    recommendation: str = Field(description="คำแนะนำการดูแลตนเองสำหรับผู้ป่วย เขียนเป็นภาษาไทย ต้องบอกชัดว่าควรทำอะไร")
    reason: str = Field(description="เหตุผลที่ประเมินระดับความเสี่ยงนี้ เขียนเป็นภาษาไทย")

class DescriptionAnalysisOutput(BaseModel):
    """Output from LLM analysis of description fields"""
    has_risk: bool = Field(description="มีสัญญาณเสี่ยงหรือไม่")
    risk_level: str = Field(description="ระดับความเสี่ยง: 'ปกติ', 'เฝ้าระวัง', 'เสี่ยง'")
    analysis: str = Field(description="การวิเคราะห์จาก LLM")
    key_points: List[str] = Field(description="ประเด็นสำคัญที่ต้องสังเกต")

class RiskSummaryOutput(BaseModel):
    """Output from LLM comprehensive summary"""
    overall_risk: str = Field(description="ความเสี่ยงโดยรวม")
    summary: str = Field(description="สรุปสำหรับผู้ป่วย: ภาษาง่าย รวมสาเหตุและคำแนะนำในข้อความเดียว")
    critical_issues: List[str] = Field(description="ปัญหาเร่งด่วน")
    
class PatientQuestionAnswer(BaseModel):
    """Output from LLM answering patient questions"""
    answer: str = Field(description="คำตอบสำหรับผู้ป่วย")
    urgency_level: str = Field(description="ระดับความเร่งด่วน: 'ปกติ', 'ติดตาม', 'เร่งด่วน'")
    should_contact_doctor: bool = Field(description="ควรติดต่อแพทย์หรือไม่")
    related_risks: List[str] = Field(description="ความเสี่ยงที่เกี่ยวข้อง")


# ------------------------------------------------------------
# 3) Build LLM Model
# ------------------------------------------------------------
def build_llm(api_key: str, model_name: str = "deepseek-chat"):
    """Build DeepSeek LLM for text analysis"""
    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url="https://api.deepseek.com",
        temperature=0.2,
        max_tokens=500
    )


# ------------------------------------------------------------
# 4) LLM-Based Analysis Functions
# ------------------------------------------------------------
def analyze_description_field(
    main_field_label: str, 
    desc_field_label: str, 
    description: str, 
    main_value: str, 
    procedures: str,
    llm
) -> DescriptionAnalysisOutput:
    """วิเคราะห์ description fields ด้วย LLM"""
    
    # Handle empty description
    if not description:
        return DescriptionAnalysisOutput(
            has_risk=False,
            risk_level="ปกติ",
            analysis="ไม่มีข้อมูลเพิ่มเติม",
            key_points=[]
        )
    
    # Convert array to string
    if isinstance(description, list):
        description = ", ".join(str(item) for item in description if item)
    
    if not description or description.strip() == "":
        return DescriptionAnalysisOutput(
            has_risk=False,
            risk_level="ปกติ",
            analysis="ไม่มีข้อมูลเพิ่มเติม",
            key_points=[]
        )
    
    # แปลง procedures (list → string)
    if procedures and procedures != 'ไม่ระบุ':
        if isinstance(procedures, list):
            proc_list = [str(p) for p in procedures if p]
            proc_str = ', '.join(proc_list) if proc_list else None
        else:
            proc_str = str(procedures)
    else:
        proc_str = None
    
    from langchain_core.output_parsers import PydanticOutputParser
    parser = PydanticOutputParser(pydantic_object=DescriptionAnalysisOutput)
    
    # สร้าง prompt แบบมี condition
    role = "คุณเป็นพยาบาลหญิงที่วิเคราะห์อาการผู้ป่วย"
    if proc_str:
        role += f"หลัง{proc_str}"
    
    prompt = f"""
{role}

【 Section: {main_field_label} 】
- คำตอบหลัก: {main_value}
- {desc_field_label}: "{description}"
{f'- หัตถการที่ทำ: {proc_str}' if proc_str else ''}

งาน: วิเคราะห์คำอธิบายเพิ่มเติมว่ามีสัญญาณเสี่ยงที่ต้องระวังหรือไม่

{parser.get_format_instructions()}
"""
     # 👇 เพิ่ม logging
    print("\n" + "="*80)
    print(f"📝 PROMPT: analyze_description_field ({main_field_label})")
    print("="*80)
    print(prompt)
    print("="*80 + "\n")
    
    try:
        response = llm.invoke(prompt)
        return parser.parse(response.content)
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        return DescriptionAnalysisOutput(
            has_risk=False,
            risk_level="ปกติ",
            analysis=f"ไม่สามารถวิเคราะห์ได้: {str(e)[:50]}",
            key_points=[]
        )


# ------------------------------------------------------------
# Helper Functions for Risk Summarization
# ------------------------------------------------------------

def _categorize_risks_by_level(all_results: Dict[str, Dict[str, str]]) -> tuple:
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
        if 'สูง' in risk_level:
            high_risk.append(f"{flow_name}: {result['reason']}")
            high_risk_flows.append((flow_name, result))
        elif 'กลาง' in risk_level or 'ปานกลาง' in risk_level:
            medium_risk.append(f"{flow_name}: {result['reason']}")
            medium_risk_flows.append((flow_name, result))
        elif 'ซับซ้อน' in risk_level or 'ไม่สามารถสรุป' in risk_level:
            complicated_risk.append(f"{flow_name}: {result['reason']}")
            complicated_risk_flows.append((flow_name, result))
        elif 'ต่ำ' in risk_level:
            low_risk.append(f"{flow_name}: {result['reason']}")
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
        str: ระดับความเสี่ยงโดยรวม
    """
    # เช็คตามลำดับความสำคัญ: สูง > กลาง > ซับซ้อน > ต่ำ
    if high_risk_count >= 1:
        return 'ความเสี่ยงสูง'
    elif medium_risk_count >= 1:
        return 'ความเสี่ยงปานกลาง'
    elif complicated_risk_count >= 1:
        # ซับซ้อน = มีอาการอื่นๆที่ผู้ป่วยระบุเพิ่มเติมที่ไม่อยู่ในตัวเลือก
        return 'ไม่สามารถสรุปผลความเสี่ยงได้เนื่องจากอาการมีความซับซ้อน'
    else:
        return 'ความเสี่ยงต่ำ'


def _build_critical_issues(high_risk_flows: List[tuple]) -> List[str]:
    """
    สร้างรายการปัญหาวิกฤติจากความเสี่ยงสูง
    
    Args:
        high_risk_flows: List of (flow_name, result) tuples
    
    Returns:
        List[str]: รายการปัญหาวิกฤติ
    """
    critical_issues = []
    for flow_name, result in high_risk_flows:
        critical_issues.append(f"⚠️ {flow_name}: {result['reason']}")
    return critical_issues


def _build_description_context(description_analysis) -> str:
    """
    สร้าง context string จากการวิเคราะห์ description fields
    
    Args:
        description_analysis: ผลการวิเคราะห์จาก LLM (dict หรือ list)
    
    Returns:
        str: Context string สำหรับใส่ใน prompt
    """
    if not description_analysis:
        return ""
    
    desc_parts = []
    
    # รองรับทั้ง dict และ list
    if isinstance(description_analysis, dict):
        for field, analysis in description_analysis.items():
            if isinstance(analysis, dict) and analysis.get('has_risk'):
                desc_parts.append(
                    f"- {field}: {analysis.get('risk_level', 'ไม่ระบุ')} - {analysis.get('analysis', '')[:100]}"
                )
    elif isinstance(description_analysis, list):
        for analysis in description_analysis:
            if isinstance(analysis, dict) and analysis.get('has_risk'):
                field = analysis.get('field', 'Unknown')
                desc_parts.append(
                    f"- {field}: {analysis.get('risk_level', 'ไม่ระบุ')} - {analysis.get('analysis', '')[:100]}"
                )
    
    if desc_parts:
        return "\n\nการวิเคราะห์คำอธิบายเพิ่มเติม:\n" + "\n".join(desc_parts)
    return ""


def _build_recommendations_context(
    high_risk_flows: List[tuple],
    medium_risk_flows: List[tuple],
    low_risk_flows: List[tuple]
) -> str:
    """
    สร้าง context string จากคำแนะนำของแต่ละ flow
    
    Args:
        high_risk_flows: List of (flow_name, result) tuples
        medium_risk_flows: List of (flow_name, result) tuples
        low_risk_flows: List of (flow_name, result) tuples
    
    Returns:
        str: Context string สำหรับใส่ใน prompt
    """
    def format_recommendation(name: str, res: dict) -> str:
        """แปลงชื่อ flow ให้เหมาะสม (แปลง "อาการอื่นๆ" เป็นอาการจริง)"""
        recommendation = res.get('recommendation', '')
        
        if not recommendation:
            return None
        
        # ถ้าชื่อ flow เป็น "อาการอื่นๆ" ให้ใช้อาการจาก reason แทน
        if 'อาการอื่นๆ' in name:
            reason = res.get('reason', '')
            # ดึงอาการที่เจาะจงจาก reason
            if reason and reason != 'ไม่มีอาการอื่นๆ':
                # ตัดส่วน "มีอาการ: " หรือ "มีอาการอื่นๆที่ผู้ป่วยระบุเพิ่มเติม: " ออก
                symptom_name = reason.replace('มีอาการ: ', '').replace('มีอาการอื่นๆที่ผู้ป่วยระบุเพิ่มเติม: ', '')
                # ตัดส่วน "และมีอาการอื่นๆ..." ออก ถ้ามี
                if ' และมีอาการอื่นๆที่ผู้ป่วยระบุเพิ่มเติม:' in symptom_name:
                    symptom_name = symptom_name.split(' และมีอาการอื่นๆที่ผู้ป่วยระบุเพิ่มเติม:')[0]
                name = symptom_name
        
        return f"- {name}: {recommendation}"
    
    high_recs = [format_recommendation(name, res) for name, res in high_risk_flows]
    high_recs = [r for r in high_recs if r]  # กรองค่า None ออก
    
    medium_recs = [format_recommendation(name, res) for name, res in medium_risk_flows]
    medium_recs = [r for r in medium_recs if r]
    
    low_recs = [format_recommendation(name, res) for name, res in low_risk_flows]
    low_recs = [r for r in low_recs if r]
    
    if not (high_recs or medium_recs or low_recs):
        return ""
    
    context = "\n\nคำแนะนำจาก Rule-based Assessment:\n"
    if high_recs:
        context += "ความเสี่ยงสูง:\n" + "\n".join(high_recs) + "\n"
    if medium_recs:
        context += "ความเสี่ยงปานกลาง:\n" + "\n".join(medium_recs) + "\n"
    if low_recs:
        context += "ความเสี่ยงต่ำ:\n" + "\n".join(low_recs)
    
    return context




def _generate_patient_summary(
    overall_risk: str,
    high_risk: List[str],
    medium_risk: List[str],
    low_risk: List[str],
    complicated_risk: List[str],
    recommendations_context: str,
    procedures: str,
    patient_name: str,
    llm
) -> str:
    """
    สร้าง summary สำหรับผู้ป่วย - แยก prompt ตามระดับความเสี่ยง
    
    Args:
        overall_risk: ระดับความเสี่ยงโดยรวม
        high_risk: รายการความเสี่ยงสูง
        medium_risk: รายการความเสี่ยงปานกลาง
        low_risk: รายการความเสี่ยงต่ำ
        complicated_risk: รายการอาการซับซ้อน
        recommendations_context: Context ของคำแนะนำจาก rule-based
        procedures: หัตถการที่ทำ
        patient_name: ชื่อผู้ป่วย
        llm: LLM instance
    
    Returns:
        str: Summary text สำหรับผู้ป่วย ตาม format ที่กำหนด
    """
    # แปลง procedures
    if procedures and procedures != 'ไม่ระบุ':
        if isinstance(procedures, list):
            proc_list = [str(p) for p in procedures if p]
            procedures_text = ', '.join(proc_list) if proc_list else ""
        else:
            procedures_text = str(procedures)
    else:
        procedures_text = ""
    
    # เตรียมข้อมูลสำหรับ prompt
    name_text = f"คุณ{patient_name}" if patient_name else ""
    
    # รวม risks ทั้งหมดเพื่อสร้างคำแนะนำ
    all_risk_items = high_risk + medium_risk + low_risk + complicated_risk
    
    # กรณีซับซ้อน: ถ้ามี error หรือไม่สามารถประเมินได้ หรือ COMPLICATED
    is_complex = any('ไม่สามารถประเมินได้' in item or 'error' in item.lower() 
                     for item in all_risk_items)
    has_complicated = 'ซับซ้อน' in overall_risk
    
    # เลือก prompt ตามระดับความเสี่ยง
    if is_complex or has_complicated:
        prompt = _build_complex_case_prompt(
            name_text, all_risk_items, recommendations_context
        )
    elif 'สูง' in overall_risk:
        prompt = _build_high_risk_prompt(
            name_text, high_risk, medium_risk, low_risk, recommendations_context
        )
    elif 'กลาง' in overall_risk or 'ปานกลาง' in overall_risk:
        prompt = _build_medium_risk_prompt(
            name_text, high_risk, medium_risk, low_risk, recommendations_context
        )
    else:  # ความเสี่ยงต่ำ
        prompt = _build_low_risk_prompt(
            name_text, all_risk_items, recommendations_context
        )
    
    print("\n" + "="*80)
    print(f"📝 PROMPT: _generate_patient_summary ({overall_risk})")
    print("="*80)
    print(prompt)
    print("="*80 + "\n")
    
    try:
        response = llm.invoke(prompt)
        return response.content.strip().replace("*", "")
    except Exception as e:
        print(f"Error generating patient summary: {e}")
        return _generate_fallback_summary_text(overall_risk, name_text)


def _build_high_risk_prompt(
    name_text: str,
    high_risk: List[str],
    medium_risk: List[str],
    low_risk: List[str],
    recommendations_context: str
) -> str:
    """สร้าง prompt สำหรับกรณีเสี่ยงสูง"""
    return f"""คุณเป็นพยาบาลที่สื่อสารกับผู้ป่วยผ่าน LINE

รายละเอียดความเสี่ยงสูง:
{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(high_risk)) if high_risk else '- ไม่มี'}

รายละเอียดความเสี่ยงปานกลาง:
{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(medium_risk)) if medium_risk else '- ไม่มี'}

รายละเอียดความเสี่ยงต่ำ:
{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(low_risk)) if low_risk else '- ไม่มี'}
{recommendations_context}

งาน: สร้างข้อความตาม FORMAT ด้านล่างนี้ให้ตรงทุกรายละเอียด

**FORMAT ที่ต้องการ:**

จากการประเมิน พบว่า{name_text} มีความเสี่ยงต่อการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปากในระดับสูง
เนื่องจาก [สรุปสาเหตุหลักจากรายละเอียดความเสี่ยงสูง]

แนะนำ:
• [หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context]
• [หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context]
แนะนำให้ติดต่อพยาบาลโดยเร็ว โทร {PHONE_NUMBER} เพื่อรับการประเมินอาการหรือนัดหมายเป็นกรณีพิเศษ

คำแนะนำเพิ่มเติมตามอาการ
• [หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context]
• [หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context]

**กฎที่ต้องปฏิบัติอย่างเคร่งครัด:**

1. **ห้ามใช้ markdown** (**, *, -, #) และ **ห้ามใช้ emoji** ทุกชนิด
2. ใช้ข้อความ plain text เท่านั้น
3. **ห้ามใส่วงเล็บ ()** ในทุกส่วน - ห้ามใส่คำอธิบายหรืออาการในวงเล็บ
4. **หัวข้ออาการ:**
   - ย่อให้สั้น 3-5 คำเท่านั้น จับคีย์เวิร์ดสำคัญ
   - ห้ามใช้ "อาการอื่นๆ" - ต้องระบุอาการชัดเจน
   - ตัวอย่างที่ถูก: "ปวดหัว", "ยาฆ่าเชื้อ", "การประคบ", "การเดิน"
   - ตัวอย่างที่ผิด: "อาการปวดหัว (ที่ยาแก้ไม่หาย)", "อาการอื่นๆ"
5. **คำแนะนำ:**
   - คัดลอกคำแนะนำเต็มจาก recommendations_context ทุกคำ
   - ห้ามขึ้นต้นด้วย "แนะนำ" - เริ่มจากการกระทำเลย
   - ตัดคำว่า "พบแพทย์", "พบพยาบาล", "ติดต่อแพทย์", "ติดต่อพยาบาล" ออก
   - ถ้าคำแนะนำมีแค่ "ติดต่อพยาบาล/แพทย์" อย่างเดียว → ข้าม ไม่แสดง
6. **ตัวอย่างที่ถูกต้อง:**
   • ปวดหัว: ทานยาแก้ปวดตามทันตแพทย์สั่ง
   • ยาฆ่าเชื้อ: รีบทานทันทีที่นึกได้ หากใกล้เวลามื้อถัดไปให้ข้ามมื้อที่ลืม
   • การประคบ: เปลี่ยนเป็นประคบเย็น
   • การเดิน: ใช้เวลา ค่อยๆ หายเอง
7. **ส่วน "แนะนำ:"** = อาการเสี่ยงสูงเท่านั้น
8. **ส่วน "คำแนะนำเพิ่มเติมตามอาการ"** = อาการเสี่ยงปานกลางและต่ำเท่านั้น (ถ้าไม่มีให้ตัดส่วนนี้ออก)
"""


def _build_medium_risk_prompt(
    name_text: str,
    high_risk: List[str],
    medium_risk: List[str],
    low_risk: List[str],
    recommendations_context: str
) -> str:
    """สร้าง prompt สำหรับกรณีเสี่ยงกลาง"""
    return f"""คุณเป็นพยาบาลที่สื่อสารกับผู้ป่วยผ่าน LINE

รายละเอียดความเสี่ยงปานกลาง:
{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(medium_risk)) if medium_risk else '- ไม่มี'}

รายละเอียดความเสี่ยงต่ำ:
{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(low_risk)) if low_risk else '- ไม่มี'}
{recommendations_context}

งาน: สร้างข้อความตาม FORMAT ด้านล่างนี้ให้ตรงทุกรายละเอียด

**FORMAT ที่ต้องการ:**

จากการประเมิน พบว่า{name_text} มีความเสี่ยงต่อการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปากระดับปานกลาง
เนื่องจาก [สรุปสาเหตุหลักจากรายละเอียดความเสี่ยงปานกลาง]

แนะนำ:
• [หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context]
• [หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context]
ทีมพยาบาลจะติดต่อกลับเพื่อประเมินอาการเพิ่มเติม สอบถามเพิ่มเติม โทร {PHONE_NUMBER}

คำแนะนำเพิ่มเติมตามอาการ
• [หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context]
• [หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context]

**กฎที่ต้องปฏิบัติอย่างเคร่งครัด:**

1. **ห้ามใช้ markdown** (**, *, -, #) และ **ห้ามใช้ emoji** ทุกชนิด
2. ใช้ข้อความ plain text เท่านั้น
3. **ห้ามใส่วงเล็บ ()** ในทุกส่วน - ห้ามใส่คำอธิบายหรืออาการในวงเล็บ
4. **หัวข้ออาการ:**
   - ย่อให้สั้น 3-5 คำเท่านั้น จับคีย์เวิร์ดสำคัญ
   - ห้ามใช้ "อาการอื่นๆ" - ต้องระบุอาการชัดเจน
   - ตัวอย่างที่ถูก: "อาการบวม", "การแปรงฟัน", "การบ้วนปาก"
   - ตัวอย่างที่ผิด: "อาการบวม (ที่ทำให้หายใจลำบาก)", "อาการอื่นๆ"
5. **คำแนะนำ:**
   - คัดลอกคำแนะนำเต็มจาก recommendations_context ทุกคำ
   - ห้ามขึ้นต้นด้วย "แนะนำ" - เริ่มจากการกระทำเลย
   - ตัดคำว่า "พบแพทย์", "พบพยาบาล", "ติดต่อแพทย์", "ติดต่อพยาบาล" ออก
   - ถ้าคำแนะนำมีแค่ "ติดต่อพยาบาล/แพทย์" อย่างเดียว → ข้าม ไม่แสดง
6. **ตัวอย่างที่ถูกต้อง:**
   • อาการบวม: ประคบอุ่นนอกช่องปาก และนอนยกศีรษะสูง 30 องศา
   • การแปรงฟัน: ใช้แปรงหัวเล็กขนนุ่ม + ยาสีฟันไม่แสบ แปรงเบาๆ หลีกเลี่ยงเหงือกที่มีแผล
   • การบ้วนปาก: บ้วนปากเบาๆด้วยน้ำเปล่าหรือน้ำยาบ้วนปาก ทุกครั้งหลังทานอาหาร
7. **ส่วน "แนะนำ:"** = อาการเสี่ยงปานกลางเท่านั้น
8. **ส่วน "คำแนะนำเพิ่มเติมตามอาการ"** = อาการเสี่ยงต่ำเท่านั้น (ถ้าไม่มีให้ตัดส่วนนี้ออก)
"""


def _build_complex_case_prompt(
    name_text: str,
    all_risk_items: List[str],
    recommendations_context: str
) -> str:
    """สร้าง prompt สำหรับกรณีซับซ้อน"""
    return f"""คุณเป็นพยาบาลที่สื่อสารกับผู้ป่วยผ่าน LINE

รายละเอียดอาการ:
{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(all_risk_items)) if all_risk_items else '- ไม่มี'}
{recommendations_context}

งาน: สร้างข้อความตาม FORMAT ด้านล่างนี้ให้ตรงทุกรายละเอียด

**FORMAT ที่ต้องการ:**

จากการประเมินความเสี่ยงในการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปาก พบว่าไม่สามารถสรุปผลความเสี่ยงได้เนื่องจากอาการมีความซับซ้อน
ทีมพยาบาลจะติดต่อกลับเพื่อประเมินอาการเพิ่มเติม หากมีข้อสงสัย โทร {PHONE_NUMBER}

คำแนะนำเบื้องต้นตามอาการ
• [หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context]
• [หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context]

**กฎที่ต้องปฏิบัติอย่างเคร่งครัด:**

1. **ห้ามใช้ markdown** (**, *, -, #) และ **ห้ามใช้ emoji** ทุกชนิด
2. ใช้ข้อความ plain text เท่านั้น
3. **ห้ามใส่วงเล็บ ()** ในทุกส่วน - ห้ามใส่คำอธิบายหรืออาการในวงเล็บ
4. **หัวข้ออาการ:**
   - ย่อให้สั้น 3-5 คำเท่านั้น จับคีย์เวิร์ดสำคัญ
   - ห้ามใช้ "อาการอื่นๆ" - ต้องระบุอาการชัดเจน
   - ตัวอย่างที่ถูก: "เลือดออก", "อาการไข้", "ลวดมัดฟัน"
   - ตัวอย่างที่ผิด: "เลือดออก (จากจมูก)", "อาการอื่นๆ"
5. **คำแนะนำ:**
   - คัดลอกคำแนะนำเต็มจาก recommendations_context ทุกคำ
   - ห้ามขึ้นต้นด้วย "แนะนำ" - เริ่มจากการกระทำเลย
   - ตัดคำว่า "พบแพทย์", "พบพยาบาล", "ติดต่อแพทย์", "ติดต่อพยาบาล" ออก
   - ถ้าคำแนะนำมีแค่ "ติดต่อพยาบาล/แพทย์" อย่างเดียว → ข้าม ไม่แสดง
6. **ตัวอย่างที่ถูกต้อง:**
   • เลือดออก: กัดผ้าก๊อซให้แน่นหากเลือดออกในช่องปาก หรือก้มหน้าและกดปีกจมูกเข้ากันหากเลือดออกจากจมูก ร่วมกับประคบเย็นนอกช่องปาก
   • อาการไข้: เช็ดตัว ทานยาลดไข้ พาราเซตามอล
   • ลวดมัดฟัน: ติดต่อพยาบาลเพื่อทำการนัดหมายกับทันตแพทย์ทันที
7. ถ้าไม่มีคำแนะนำเพิ่มเติม ให้ตัดส่วน "คำแนะนำเบื้องต้นตามอาการ" ทั้งหมดออก

"""


def _build_low_risk_prompt(
    name_text: str,
    all_risk_items: List[str],
    recommendations_context: str
) -> str:
    """สร้าง prompt สำหรับกรณีเสี่ยงต่ำ"""
    return f"""คุณเป็นพยาบาลที่สื่อสารกับผู้ป่วยผ่าน LINE

รายละเอียดอาการ:
{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(all_risk_items)) if all_risk_items else '- ไม่มี'}
{recommendations_context}

งาน: สร้างข้อความตาม FORMAT ด้านล่างนี้ให้ตรงทุกรายละเอียด

**FORMAT ที่ต้องการ:**

จากผลประเมินพบว่ามีความเสี่ยงในการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปาก ระดับต่ำ
อาการโดยรวมอยู่ในเกณฑ์ปกติ

คำแนะนำเบื้องต้นตามอาการ
[หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context]
[หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context]

หากมีข้อสงสัย โทร {PHONE_NUMBER}

**กฎที่ต้องปฏิบัติอย่างเคร่งครัด:**

1. **ห้ามใช้ markdown** (**, *, -, •, #) และ **ห้ามใช้ emoji** ทุกชนิด
2. ใช้ข้อความ plain text เท่านั้น
3. **ห้ามใส่วงเล็บ ()** ในทุกส่วน - ห้ามใส่คำอธิบายหรืออาการในวงเล็บ
4. **ห้ามใช้ bullet point (•)** - ใช้รูปแบบ "หัวข้อ: คำแนะนำ" เท่านั้น
5. **หัวข้ออาการ:**
   - ย่อให้สั้น 3-5 คำเท่านั้น จับคีย์เวิร์ดสำคัญ
   - ห้ามใช้ "อาการอื่นๆ" - ต้องระบุอาการชัดเจน
   - ตัวอย่างที่ถูก: "อาการชา", "การแปรงฟัน", "การบ้วนปาก"
   - ตัวอย่างที่ผิด: "อาการชา (บริเวณริมฝีปาก)", "อาการอื่นๆ"
6. **คำแนะนำ:**
   - คัดลอกคำแนะนำเต็มจาก recommendations_context ทุกคำ
   - ห้ามขึ้นต้นด้วย "แนะนำ" - เริ่มจากการกระทำเลย
   - ตัดคำว่า "พบแพทย์", "พบพยาบาล", "ติดต่อแพทย์", "ติดต่อพยาบาล" ออก
   - ถ้าคำแนะนำมีแค่ "ติดต่อพยาบาล/แพทย์" อย่างเดียว → ข้าม ไม่แสดง
7. **ตัวอย่างที่ถูกต้อง:**
   อาการชา: สังเกตอาการ หากชานานเกิน 2 สัปดาห์ ควรพบทันตแพทย์
   การแปรงฟัน: ใช้แปรงหัวเล็กขนนุ่ม + ยาสีฟันไม่แสบ แปรงเบาๆ หลีกเลี่ยงเหงือกที่มีแผล
   การบ้วนปาก: บ้วนปากเบาๆด้วยน้ำเปล่าหรือน้ำยาบ้วนปาก ทุกครั้งหลังทานอาหาร
8. ถ้าไม่มีคำแนะนำเพิ่มเติม ให้ตัดส่วน "คำแนะนำเบื้องต้นตามอาการ" ทั้งหมดออก
"""


def _generate_fallback_summary_text(overall_risk: str, name_text: str) -> str:
    """สร้าง fallback text เมื่อ LLM error"""
    if 'สูง' in overall_risk:
        return f"""จากการประเมิน พบว่า{name_text}มีความเสี่ยงต่อการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปากในระดับสูง

แนะนำ:
แนะนำให้ติดต่อพยาบาลโดยเร็ว โทรศัพท์ {PHONE_NUMBER}"""
    elif 'กลาง' in overall_risk or 'ปานกลาง' in overall_risk:
        return f"""จากการประเมิน พบว่า{name_text}มีความเสี่ยงต่อการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปากระดับปานกลาง

แนะนำ:
ทีมพยาบาลจะติดต่อกลับเพื่อประเมินอาการเพิ่มเติมค่ะ
สอบถามเพิ่มเติม โทร {PHONE_NUMBER}"""
    else:
        return """จากผลประเมินพบว่ามีความเสี่ยงในการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปาก ระดับต่ำ
อาการโดยรวมอยู่ในเกณฑ์ปกติ

หากมีข้อสงสัย โทร {PHONE_NUMBER}"""


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
    critical_issues: List[str]
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
    for flow_name, result in high_risk_flows:
        if result['recommendation']:
            rec_parts.append(result['recommendation'])
    for flow_name, result in medium_risk_flows:
        if result['recommendation']:
            rec_parts.append(result['recommendation'])
    
    if patient_summary_parts:
        summary = " ".join(patient_summary_parts)
        if rec_parts:
            summary += " คำแนะนำ: " + " ".join(rec_parts[:3])  # Top 3 recommendations
    else:
        summary = "อาการอยู่ในเกณฑ์ปกติ ดูแลตามคำแนะนำจากแพทย์"
    
    return RiskSummaryOutput(
        overall_risk=overall_risk,
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
    description_analysis: Dict[str, Any] = None,
    procedures: str = None
) -> RiskSummaryOutput:
    """
    สรุปผลการประเมินจากทุก flows โดยใช้ rule-based คำนวณ overall risk 
    และใช้ LLM สรุป "เหตุผล" และ "คำแนะนำ" พร้อมรวม context จาก description analysis
    
    Args:
        all_results: ผลการประเมินจากทุก flows {flow_name: {risk_level, reason, recommendation}}
        llm: LLM instance (ใช้สำหรับสรุป summary และ recommendations)
        patient_data: ข้อมูลผู้ป่วยเดิม (optional) - ควรมี 'name' field
        description_analysis: ผลการวิเคราะห์จาก analyze_description_field (optional)
        procedures: หัตถการที่ผู้ป่วยเข้ารับ (optional)
    
    Returns:
        RiskSummaryOutput object containing overall_risk, summary, recommendations, critical_issues
    """
    # 1. แยกตามระดับควาวามเสี่ยง
    (high_risk, high_risk_flows, medium_risk, 
     medium_risk_flows, low_risk, low_risk_flows,
     complicated_risk, complicated_risk_flows) = _categorize_risks_by_level(all_results)
    
    # 2. คำนวณความเสี่ยงโดยรวม (Rule-based)
    overall_risk = _calculate_overall_risk(len(high_risk), len(medium_risk), len(complicated_risk))
    
    # 3. สร้าง Critical Issues
    critical_issues = _build_critical_issues(high_risk_flows)
    
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
            critical_issues
        )
    
    # 6. สร้าง context strings สำหรับ LLM
    description_context = _build_description_context(description_analysis)
    recommendations_context = _build_recommendations_context(
        high_risk_flows, medium_risk_flows, low_risk_flows
    )
    
    # 7. เรียก LLM สร้าง summary สำหรับผู้ป่วย
    try:
        # Generate patient summary (easy language + recommendations)
        summary = _generate_patient_summary(
            overall_risk, high_risk, medium_risk, low_risk, complicated_risk,
            recommendations_context, procedures, patient_name, llm
        )
        
        return RiskSummaryOutput(
            overall_risk=overall_risk,
            summary=summary,
            critical_issues=critical_issues
        )
    except Exception as e:
        print(f"Error in LLM summarization: {str(e)}")
        return _create_fallback_summary(
            overall_risk, high_risk, medium_risk, low_risk,
            high_risk_flows, medium_risk_flows, low_risk_flows,
            critical_issues
        )


def answer_patient_questions(
    question: str, 
    patient_context: dict, 
    llm,
    risk_results: Dict[str, Dict[str, str]] = None,
    procedures: str = None
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
    
    prompt = f"""
{role}

{f'ข้อมูลผู้ป่วย: {context_str}' if context_str else ''}{risk_context}

คำถามจากผู้ป่วย:
"{question}"

งาน: ตอบคำถามสั้นๆ เหมือนส่งผ่าน LINE

**กฎสำคัญ:**
1. **ตอบสั้นมาก** - เริ่มด้วยคำตอบตรงๆ 
2. **ไม่ต้องเรียก** "คุณคะ" หรือ "กรุณา" (เป็นกันเองแบบ LINE)
3. ถ้าเร่งด่วน: ใช้ "แจ้งทันตแพทย์ทันที" (ไม่ต้องพูดยืดยาว)
4. ถ้าไม่เร่งด่วน: ตอบตรงๆ พร้อมคำแนะนำสั้นๆ

ตัวอย่าง:
- คำถาม: "หายใจลำบากควรทำอย่างไร?"
- คำตอบ: "อาการนี้เร่งด่วนมาก แจ้งทันตแพทย์ทันทีนะคะ"

- คำถาม: "ควรประคบนานแค่ไหน?"
- คำตอบ: "ประคบครั้งละ 15-20 นาที วันละ 3-4 ครั้ง โดยเฉพาะหลังอาหารค่ะ"

- คำถาม: "อาการชาจะหายเมื่อไหร่?"
- คำตอบ: "ปกติจะค่อยๆ ดีขึ้นใน 2-3 สัปดาห์ ถ้ายังไม่ดีขึ้นให้แจ้งทันตแพทย์นะคะ"

{format_instructions}
"""
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
def classify_risk(input_data: dict, api_key: str = None, flow: str = None, flow_name: str = None, llm=None, max_retries: int = 3):
    """
    Classify risk using Rule Engine (deterministic)
    Args:
        input_data: Patient data dictionary
        api_key: Google API key (optional, kept for backward compatibility)
        flow: Risk flow criteria (kept for backward compatibility, not used)
        flow_name: Name of the flow to evaluate
        llm: Pre-built LLM instance (optional, kept for backward compatibility)
        max_retries: Maximum number of retries (kept for backward compatibility)
    """
    # Use Rule Engine for deterministic classification
    engine = RuleEngine()
    
    try:
        # Rule-based evaluation (deterministic)
        result = engine.evaluate_flow(flow_name, input_data)
        
        # Convert to OutputRiskClassification format
        return OutputRiskClassification(
            risk_level=result['risk_level'],
            recommendation=result['recommendation'],
            reason=result['reason']
        )
        
    except Exception as e:
        print(f"Error in rule-based classification for {flow_name}: {str(e)}")
        
        # Fallback to default response
        return OutputRiskClassification(
            risk_level="ไม่สามารถประเมินได้",
            recommendation="กรุณาติดต่อทีมแพทย์เพื่อประเมินเพิ่มเติม",
            reason=f"ไม่สามารถประเมินได้: {str(e)[:100]}"
        )


# Async version for concurrent processing
async def classify_risk_async(input_data: dict, llm, flow: str, flow_name: str, semaphore, max_retries: int = 3):
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
                lambda: engine.evaluate_flow(flow_name, input_data)
            )
            
            # Convert to OutputRiskClassification format
            result = OutputRiskClassification(
                risk_level=result_dict['risk_level'],
                recommendation=result_dict['recommendation'],
                reason=result_dict['reason']
            )
            
            return flow_name, result
            
        except Exception as e:
            print(f"Error in flow {flow_name}: {str(e)}")
            
            # Return default safe response
            default_response = OutputRiskClassification(
                risk_level="ไม่สามารถประเมินได้",
                recommendation="กรุณาติดต่อทีมแพทย์เพื่อประเมินเพิ่มเติม",
                reason=f"ไม่สามารถประเมินได้: {str(e)[:100]}"
            )
            return flow_name, default_response





