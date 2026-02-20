"""
Prompt templates for LLM-based risk analysis
LLM role: generate ONLY the risk_summary clause (after "due to" / "เนื่องจาก")
Output is Pydantic-controlled via format_instructions.
"""
from typing import List
from app.core.constants import PHONE_NUMBER


def build_description_analysis_prompt(
    main_field_label: str,
    desc_field_label: str,
    description: str,
    main_value: str,
    proc_str: str = None,
    format_instructions: str = ""
) -> str:
    """สร้าง prompt สำหรับวิเคราะห์ description fields"""

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

{format_instructions}
"""
    return prompt


def build_high_risk_prompt(
    high_risk: List[str],
    language: str = 'th',
    format_instructions: str = ""
) -> str:
    """LLM generates ONLY the 'due to' clause for HIGH risk — Pydantic-controlled output."""

    risk_lines = []
    if high_risk:
        risk_lines.append("HIGH RISK:" if language == 'en' else "ความเสี่ยงสูง:")
        for item in high_risk:
            risk_lines.append(f"  - {item}")

    risk_text = "\n".join(risk_lines)

    if language == 'en':
        return f"""You are a nurse writing a patient message. The patient has HIGH risk.

Risk assessment:
{risk_text}

Task: Write summarizing the main HIGH RISK reasons based ONLY on the provided assessment.
This completes: "...HIGH risk of complications due to [YOUR ANSWER]."
Do NOT embellish or add information not present in the assessment. Your ONLY role is to connect the provided reasons.


Do NOT include "due to" in your answer.
Do NOT include recommendations.
Do NOT analyze or explain further.

{format_instructions}
"""
    else:
        return f"""คุณเป็นพยาบาล กำลังเขียนข้อความให้ผู้ป่วยที่มีความเสี่ยงสูง

ผลการประเมิน:
{risk_text}

งาน: เขียนสรุปสาเหตุหลักของความเสี่ยงสูง โดยอ้างอิงจากผลการประเมินที่ให้มาเท่านั้น
จะต่อท้าย: "...เนื่องจาก [คำตอบของคุณ]"
ห้ามแต่งเติมข้อมูลที่ไม่มีในการประเมิน หน้าที่ของคุณคือเชื่อมโยงเหตุผลเหล่านี้เข้าด้วยกันเท่านั้น


ห้ามใส่คำว่า "เนื่องจาก" ในคำตอบ
ห้ามใส่คำแนะนำ
ห้ามวิเคราะห์หรืออธิบายเพิ่มเติม

{format_instructions}
"""


def build_medium_risk_prompt(
    medium_risk: List[str],
    language: str = 'th',
    format_instructions: str = ""
) -> str:
    """LLM generates ONLY the 'due to' clause for MODERATE risk — Pydantic-controlled output."""

    risk_lines = []
    if medium_risk:
        risk_lines.append("MODERATE RISK:" if language == 'en' else "ความเสี่ยงปานกลาง:")
        for item in medium_risk:
            risk_lines.append(f"  - {item}")

    risk_text = "\n".join(risk_lines)

    if language == 'en':
        return f"""You are a nurse writing a patient message. The patient has MODERATE risk.

Risk assessment:
{risk_text}

Task: Write summarizing the main MODERATE RISK reasons based ONLY on the provided assessment.
This phrase completes: "...MODERATE risk of complications due to [YOUR ANSWER]."
Do NOT embellish or add information not present in the assessment. Your ONLY role is to connect the provided reasons.


Do NOT include "due to" in your answer.
Do NOT include recommendations.

{format_instructions}
"""
    else:
        return f"""คุณเป็นพยาบาล กำลังเขียนข้อความให้ผู้ป่วยที่มีความเสี่ยงปานกลาง

ผลการประเมิน:
{risk_text}

งาน: เขียนสรุปสาเหตุหลักของความเสี่ยงปานกลาง โดยอ้างอิงจากผลการประเมินที่ให้มาเท่านั้น
จะต่อท้าย: "...เนื่องจาก [คำตอบของคุณ]"
ห้ามแต่งเติมข้อมูลที่ไม่มีในการประเมิน หน้าที่ของคุณคือเชื่อมโยงเหตุผลเหล่านี้เข้าด้วยกันเท่านั้น


ห้ามใส่คำว่า "เนื่องจาก" ในคำตอบ
ห้ามใส่คำแนะนำ

{format_instructions}
"""


def build_patient_question_prompt(
    question: str,
    context_str: str = None,
    risk_context: str = "",
    proc_str: str = None,
    format_instructions: str = "",
    language: str = 'th'
) -> str:
    """สร้าง prompt สำหรับตอบคำถามผู้ป่วย"""

    if language == 'en':
        role = "You are an expert female nurse taking care of a patient"
        if proc_str:
            role += f" after {proc_str}"

        return f"""
{role}

{f'Patient Data: {context_str}' if context_str else ''}{risk_context}

Question from patient:
"{question}"

Task: Answer shortly, like chatting on LINE.

Important Rules:
1. Very short answer — start with direct answer.
2. No formal address like "Sir/Madam" (friendly LINE style).
3. If urgent: use "Inform dentist immediately."
4. If not urgent: answer directly with short advice.

Examples:
- Q: "Hard to breathe, what should I do?"
  A: "This is urgent. Inform dentist immediately."
- Q: "How long to compress?"
  A: "Compress 15-20 mins, 3-4 times a day, after meals."
- Q: "When will numbness go away?"
  A: "Usually better in 2-3 weeks. If not, tell dentist."

{format_instructions}
"""

    role = "คุณเป็นพยาบาลหญิงผู้เชี่ยวชาญด้านการดูแลผู้ป่วย"
    if proc_str:
        role += f"หลัง{proc_str}"

    prompt = f"""
{role}

{f'ข้อมูลผู้ป่วย: {context_str}' if context_str else ''}{risk_context}

คำถามจากผู้ป่วย:
"{question}"

งาน: ตอบคำถามสั้นๆ เหมือนส่งผ่าน LINE

กฎสำคัญ:
1. ตอบสั้นมาก — เริ่มด้วยคำตอบตรงๆ
2. ไม่ต้องเรียก "คุณคะ" หรือ "กรุณา"
3. ถ้าเร่งด่วน: ใช้ "แจ้งทันตแพทย์ทันที"
4. ถ้าไม่เร่งด่วน: ตอบตรงๆ พร้อมคำแนะนำสั้นๆ

ตัวอย่าง:
- คำถาม: "หายใจลำบากควรทำอย่างไร?"
  คำตอบ: "อาการนี้เร่งด่วนมาก แจ้งทันตแพทย์ทันทีนะคะ"
- คำถาม: "ควรประคบนานแค่ไหน?"
  คำตอบ: "ประคบครั้งละ 15-20 นาที วันละ 3-4 ครั้ง โดยเฉพาะหลังอาหาร"

{format_instructions}
"""
    return prompt
