"""
Prompt templates for LLM-based risk analysis
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
    medium_risk: List[str],
    low_risk: List[str],
    recommendations_context: str,
    name_text: str = "",
    language: str = 'th'
) -> str:
    """สร้าง prompt สำหรับกรณีเสี่ยงสูง"""
    
    if language == 'en':
        return f"""You are a nurse communicating with a patient via LINE using English.

HIGH RISK DETAILS:
{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(high_risk)) if high_risk else '- None'}

MODERATE RISK DETAILS:
{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(medium_risk)) if medium_risk else '- None'}

LOW RISK DETAILS:
{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(low_risk)) if low_risk else '- None'}
{recommendations_context}

TASK: Generate a message following the FORMAT below strictly.

**REQUIRED FORMAT:**

Based on the assessment, {name_text if name_text else 'the patient'} has a HIGH risk of post-operative complications.
Reason: [Summarize main reasons from HIGH RISK DETAILS]

Recommendation:
• [Short Topic 3-5 words]: [Full recommendation from context]
• [Short Topic 3-5 words]: [Full recommendation from context]

Please contact a nurse immediately at {PHONE_NUMBER} for further assessment or special appointment.

Additional recommendations based on symptoms:
• [Short Topic 3-5 words]: [Full recommendation from context]
• [Short Topic 3-5 words]: [Full recommendation from context]

**STRICT RULES:**

0. **CRITICAL: Use ONLY recommendations from "Rule-based Assessment Recommendations:" section above.** 
   - DO NOT create, invent, or generate any new recommendations.
   - If a symptom has NO recommendation in the context -> SKIP IT COMPLETELY.
   - Copy recommendations EXACTLY as written - word for word.
   
1. **Section Removal Rules:**
   - If "High Risk: - No recommendations." → Remove entire "Recommendation:" section.
   - If "Medium Risk: - No recommendations." AND "Low Risk: - No recommendations." → Remove entire "Additional recommendations based on symptoms:" section.
   - If BOTH sections are removed → Keep only: risk level statement + reason + phone contact line.
   
2. **NO markdown** (**, *, -, #) and **NO emojis**.
3. Use Plain Text only.
4. **NO PARENTHESES ()** in any part.
5. **Symptom Topics:**
   - Short 3-5 words only. Capture keywords.
   - NO "Other symptoms". Must specify.
   - Good: "Headache", "Antibiotics", "Compress", "Walking"
   - Bad: "Headache (not cured by meds)", "Other symptoms"
6. **Recommendations:**
   - Copy full recommendation from context.
   - Do NOT start with "Recommend". Start with action verb.
   - Remove words like "See doctor", "See nurse", "Contact doctor".
   - If recommendation is ONLY "Contact nurse/doctor" -> Skip.
   - If NO recommendation exists for this symptom in context -> Skip.
7. **Correct Examples:**
   • Headache: Take painkillers as prescribed by dentist
   • Antibiotics: Take immediately when remembered
   • Compress: Switch to cold compress
8. **"Recommendation:" Section** = High risk symptoms only. If High Risk has no recommendations, this section MUST BE REMOVED.
9. **"Additional recommendations" Section** = Moderate/Low risk symptoms only. If both Medium and Low have no recommendations, this section MUST BE REMOVED.
"""

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
• [หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context].
• [หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context].

แนะนำให้ติดต่อพยาบาลโดยเร็ว โทร {PHONE_NUMBER} เพื่อรับการประเมินอาการหรือนัดหมายเป็นกรณีพิเศษ

คำแนะนำเพิ่มเติมตามอาการ
• [หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context].
• [หัวข้อสั้นๆ 3-5 คำ]: [คำแนะนำเต็มจาก recommendations_context].

**กฎที่ต้องปฏิบัติอย่างเคร่งครัด:**

0. **สำคัญมาก: ใช้เฉพาะคำแนะนำจาก "คำแนะนำจาก Rule-based Assessment:" ด้านบนเท่านั้น**
   - ห้ามแต่ง ห้ามสร้าง ห้ามคิดคำแนะนำใหม่ขึ้นมาเอง
   - ถ้าอาการใดไม่มีคำแนะนำใน context -> ข้ามอาการนั้นไปเลย ไม่ต้องแสดง
   - คัดลอกคำแนะนำตามที่ให้มาทุกคำ ทุกตัวอักษร
   
1. **กฎการตัดส่วน:**
   - ถ้า "ความเสี่ยงสูง: - ไม่มีคำแนะนำ" → ตัดส่วน "แนะนำ:" ทั้งหมดออก
   - ถ้า "ความเสี่ยงปานกลาง: - ไม่มีคำแนะนำ" และ "ความเสี่ยงต่ำ: - ไม่มีคำแนะนำ" → ตัดส่วน "คำแนะนำเพิ่มเติมตามอาการ" ทั้งหมดออก
   - ถ้าทั้ง 2 ส่วนถูกตัดออก → เหลือแค่: ระดับความเสี่ยง + เหตุผล + บรรทัดติดต่อโทรศัพท์
   
2. **ห้ามใช้ markdown** (**, *, -, #) และ **ห้ามใช้ emoji** ทุกชนิด
3. ใช้ข้อความ plain text เท่านั้น
4. **ห้ามใส่วงเล็บ ()** ในทุกส่วน - ห้ามใส่คำอธิบายหรืออาการในวงเล็บ
5. **หัวข้ออาการ:**
   - ย่อให้สั้น 3-5 คำเท่านั้น จับคีย์เวิร์ดสำคัญ
   - ห้ามใช้ "อาการอื่นๆ" - ต้องระบุอาการชัดเจน
   - ตัวอย่างที่ถูก: "ปวดหัว", "ยาฆ่าเชื้อ", "การประคบ", "การเดิน"
   - ตัวอย่างที่ผิด: "อาการปวดหัว (ที่ยาแก้ไม่หาย)", "อาการอื่นๆ"
6. **คำแนะนำ:**
   - คัดลอกคำแนะนำเต็มจาก recommendations_context ทุกคำ
   - ห้ามขึ้นต้นด้วย "แนะนำ" - เริ่มจากการกระทำเลย
   - ตัดคำว่า "พบแพทย์", "พบพยาบาล", "ติดต่อแพทย์", "ติดต่อพยาบาล" ออก
   - ถ้าคำแนะนำมีแค่ "ติดต่อพยาบาล/แพทย์" อย่างเดียว → ข้าม ไม่แสดง
   - ถ้าไม่มีคำแนะนำสำหรับอาการนี้ใน context → ข้าม ไม่แสดง
7. **ตัวอย่างที่ถูกต้อง:**
   • ปวดหัว: ทานยาแก้ปวดตามทันตแพทย์สั่ง
   • ยาฆ่าเชื้อ: รีบทานทันทีที่นึกได้ หากใกล้เวลามื้อถัดไปให้ข้ามมื้อที่ลืม
   • การประคบ: เปลี่ยนเป็นประคบเย็น
   • การเดิน: ใช้เวลา ค่อยๆ หายเอง
8. **ส่วน "แนะนำ:"** = อาการเสี่ยงสูงเท่านั้น ถ้าความเสี่ยงสูงไม่มีคำแนะนำ ต้องตัดส่วนนี้ออก
9. **ส่วน "คำแนะนำเพิ่มเติมตามอาการ"** = อาการเสี่ยงปานกลางและต่ำเท่านั้น ถ้าทั้งปานกลางและต่ำไม่มีคำแนะนำ ต้องตัดส่วนนี้ออก
"""


def build_medium_risk_prompt(
    medium_risk: List[str],
    low_risk: List[str],
    recommendations_context: str,
    name_text: str = "",
    language: str = 'th'
) -> str:
    """สร้าง prompt สำหรับกรณีเสี่ยงกลาง"""
    
    if language == 'en':
         return f"""You are a nurse communicating with a patient via LINE using English.

MODERATE RISK DETAILS:
{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(medium_risk)) if medium_risk else '- None'}

LOW RISK DETAILS:
{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(low_risk)) if low_risk else '- None'}
{recommendations_context}

TASK: Generate a message following the FORMAT below strictly.

**REQUIRED FORMAT:**

Based on the assessment, {name_text if name_text else 'the patient'} has a MODERATE risk of post-operative complications.
Reason: [Summarize main reasons from MODERATE RISK DETAILS]

Recommendation:
• [Short Topic 3-5 words]: [Full recommendation from context]
• [Short Topic 3-5 words]: [Full recommendation from context]

The nursing team will contact you for further assessment. For inquiries, call {PHONE_NUMBER}

Additional recommendations based on symptoms:
• [Short Topic 3-5 words]: [Full recommendation from context]
• [Short Topic 3-5 words]: [Full recommendation from context]   

**STRICT RULES:**

0. **CRITICAL: Use ONLY recommendations from "Rule-based Assessment Recommendations:" section above.** 
   - DO NOT create, invent, or generate any new recommendations.
   - If a symptom has NO recommendation in the context -> SKIP IT COMPLETELY.
   - Copy recommendations EXACTLY as written - word for word.
   
1. **Section Removal Rules:**
   - If "Medium Risk: - No recommendations." → Remove entire "Recommendation:" section.
   - If "Low Risk: - No recommendations." → Remove entire "Additional recommendations based on symptoms:" section.
   - If BOTH sections are removed → Keep only: risk level statement + reason + phone contact line.
   
2. **NO markdown** (**, *, -, #) and **NO emojis**.
3. Use Plain Text only.
4. **NO PARENTHESES ()** in any part.
5. **Symptom Topics:**
   - Short 3-5 words only.
   - NO "Other symptoms".
   - Good: "Swelling", "Brushing", "Rinsing"
   - Bad: "Swelling (hard to breathe)", "Other symptoms"
6. **Recommendations:**
   - Copy full recommendation from context.
   - Remove "See doctor", "Contact nurse".
   - If recommendation is ONLY "Contact nurse/doctor" -> Skip.
   - If NO recommendation exists for this symptom in context -> Skip.
7. **Correct Examples:**
   • Swelling: Warm compress outside mouth and sleep with head elevated 30 degrees
   • Brushing: Use small soft brush + non-stinging toothpaste, brush gently avoiding wound
   • Rinsing: Rinse gently with water or mouthwash after every meal
8. **"Recommendation:" Section** = Moderate risk symptoms only. If Medium Risk has no recommendations, this section MUST BE REMOVED.
9. **"Additional recommendations" Section** = Low risk symptoms only. If Low Risk has no recommendations, this section MUST BE REMOVED.
"""

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

0. **สำคัญมาก: ใช้เฉพาะคำแนะนำจาก "คำแนะนำจาก Rule-based Assessment:" ด้านบนเท่านั้น**
   - ห้ามแต่ง ห้ามสร้าง ห้ามคิดคำแนะนำใหม่ขึ้นมาเอง
   - ถ้าอาการใดไม่มีคำแนะนำใน context → ข้ามอาการนั้นไป ไม่ต้องแสดง
   - คัดลอกคำแนะนำตามที่ให้มาทุกคำ ทุกตัวอักษร
   
1. **กฎการตัดส่วน:**
   - ถ้า "ความเสี่ยงปานกลาง: - ไม่มีคำแนะนำ" → ตัดส่วน "แนะนำ:" ทั้งหมดออก
   - ถ้า "ความเสี่ยงต่ำ: - ไม่มีคำแนะนำ" → ตัดส่วน "คำแนะนำเพิ่มเติมตามอาการ" ทั้งหมดออก
   - ถ้าทั้ง 2 ส่วนถูกตัดออก → เหลือแค่: ระดับความเสี่ยง + เหตุผล + บรรทัดติดต่อโทรศัพท์
   
2. **ห้ามใช้ markdown** (**, *, -, #) และ **ห้ามใช้ emoji** ทุกชนิด
3. ใช้ข้อความ plain text เท่านั้น
4. **ห้ามใส่วงเล็บ ()** ในทุกส่วน - ห้ามใส่คำอธิบายหรืออาการในวงเล็บ
5. **หัวข้ออาการ:**
   - ย่อให้สั้น 3-5 คำเท่านั้น จับคีย์เวิร์ดสำคัญ
   - ห้ามใช้ "อาการอื่นๆ" - ต้องระบุอาการชัดเจน
   - ตัวอย่างที่ถูก: "อาการบวม", "การแปรงฟัน", "การบ้วนปาก"
   - ตัวอย่างที่ผิด: "อาการบวม (ที่ทำให้หายใจลำบาก)", "อาการอื่นๆ"
6. **คำแนะนำ:**
   - คัดลอกคำแนะนำเต็มจาก recommendations_context ทุกคำ
   - ห้ามขึ้นต้นด้วย "แนะนำ" - เริ่มจากการกระทำเลย
   - ตัดคำว่า "พบแพทย์", "พบพยาบาล", "ติดต่อแพทย์", "ติดต่อพยาบาล" ออก
   - ถ้าคำแนะนำมีแค่ "ติดต่อพยาบาล/แพทย์" อย่างเดียว → ข้าม ไม่แสดง
   - ถ้าไม่มีคำแนะนำสำหรับอาการนี้ใน context → ข้าม ไม่แสดง
7. **ตัวอย่างที่ถูกต้อง:**
   • อาการบวม: ประคบอุ่นนอกช่องปาก และนอนยกศีรษะสูง 30 องศา
   • การแปรงฟัน: ใช้แปรงหัวเล็กขนนุ่ม + ยาสีฟันไม่แสบ แปรงเบาๆ หลีกเลี่ยงเหงือกที่มีแผล
   • การบ้วนปาก: บ้วนปากเบาๆด้วยน้ำเปล่าหรือน้ำยาบ้วนปาก ทุกครั้งหลังทานอาหาร
8. **ส่วน "แนะนำ:"** = อาการเสี่ยงปานกลางเท่านั้น ถ้าความเสี่ยงปานกลางไม่มีคำแนะนำ ต้องตัดส่วนนี้ออก
9. **ส่วน "คำแนะนำเพิ่มเติมตามอาการ"** = อาการเสี่ยงต่ำเท่านั้น ถ้าความเสี่ยงต่ำไม่มีคำแนะนำ ต้องตัดส่วนนี้ออก
"""
    return base_prompt


def build_complex_case_prompt(
    all_risk_items: List[str],
    recommendations_context: str,
    language: str = 'th'
) -> str:
    """สร้าง prompt สำหรับกรณีซับซ้อน"""
    
    if language == 'en':
        return f"""You are a nurse communicating with a patient via LINE using English.

SYMPTOM DETAILS:
{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(all_risk_items)) if all_risk_items else '- None'}
{recommendations_context}

TASK: Generate a message following the FORMAT below strictly.

**REQUIRED FORMAT:**

Based on the assessment of post-operative complications, the risk cannot be concluded due to complex symptoms.

The nursing team will contact you for further assessment. If you have questions, call {PHONE_NUMBER}

Preliminary recommendations based on symptoms:
• [Short Topic 3-5 words]: [Full recommendation from context]
• [Short Topic 3-5 words]: [Full recommendation from context]

**STRICT RULES:**

0. **CRITICAL: Use ONLY recommendations from "Rule-based Assessment Recommendations:" section above.** 
   - DO NOT create, invent, or generate any new recommendations.
   - If a symptom has NO recommendation in the context -> SKIP IT COMPLETELY.
   - Copy recommendations EXACTLY as written - word for word.
   
1. **If "Rule-based Assessment Recommendations: No specific recommendations." OR if there are NO recommendations listed:**
   - Remove the entire "Preliminary recommendations based on symptoms:" section.
   - Keep only: risk statement + phone contact line.
   
2. **NO markdown** (**, *, -, #) and **NO emojis**.
3. Use Plain Text only.
4. **NO PARENTHESES ()** in any part.
5. **Symptom Topics:**
   - Short 3-5 words only.
   - NO "Other symptoms".
   - Good: "Bleeding", "Fever", "Wire"
   - Bad: "Bleeding (from nose)", "Other symptoms"
6. **Recommendations:**
   - Copy full recommendation from context.
   - Remove "See doctor", "Contact nurse".
   - If recommendation is ONLY "Contact nurse/doctor" -> Skip.
   - If NO recommendation exists for this symptom in context -> Skip.
7. **Correct Examples:**
   • Bleeding: Bite gauze tightly if bleeding in mouth, or tilt head down and pinch nose wings if bleeding from nose, along with cold compress outside mouth
   • Fever: Wipe body, take paracetamol
   • Wire: Contact nurse to make appointment with dentist immediately
"""

    base_prompt = f"""คุณเป็นพยาบาลที่สื่อสารกับผู้ป่วยผ่าน LINE

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

0. **สำคัญมาก: ใช้เฉพาะคำแนะนำจาก "คำแนะนำจาก Rule-based Assessment:" ด้านบนเท่านั้น**
   - ห้ามแต่ง ห้ามสร้าง ห้ามคิดคำแนะนำใหม่ขึ้นมาเอง
   - ถ้าอาการใดไม่มีคำแนะนำใน context → ข้ามอาการนั้นไป ไม่ต้องแสดง
   - คัดลอกคำแนะนำตามที่ให้มาทุกคำ ทุกตัวอักษร
   
1. **กฎการตัดส่วน:**
   - ถ้าไม่มีคำแนะนำเลย (ทุกอาการเป็น "- ไม่มีคำแนะนำ") → ตัดส่วน "คำแนะนำเบื้องต้นตามอาการ:" ทั้งหมดออก
   - เหลือแค่: ข้อความอาการซับซ้อน + บรรทัดติดต่อโทรศัพท์
   
2. **ห้ามใช้ markdown** (**, *, -, #) และ **ห้ามใช้ emoji** ทุกชนิด
3. ใช้ข้อความ plain text เท่านั้น
4. **ห้ามใส่วงเล็บ ()** ในทุกส่วน - ห้ามใส่คำอธิบายหรืออาการในวงเล็บ
5. **หัวข้ออาการ:**
   - ย่อให้สั้น 3-5 คำเท่านั้น จับคีย์เวิร์ดสำคัญ
   - ห้ามใช้ "อาการอื่นๆ" - ต้องระบุอาการชัดเจน
   - ตัวอย่างที่ถูก: "เลือดออก", "อาการไข้", "ลวดมัดฟัน"
   - ตัวอย่างที่ผิด: "เลือดออก (จากจมูก)", "อาการอื่นๆ"
6. **คำแนะนำ:**
   - คัดลอกคำแนะนำเต็มจาก recommendations_context ทุกคำ
   - ห้ามขึ้นต้นด้วย "แนะนำ" - เริ่มจากการกระทำเลย
   - ตัดคำว่า "พบแพทย์", "พบพยาบาล", "ติดต่อแพทย์", "ติดต่อพยาบาล" ออก
   - ถ้าคำแนะนำมีแค่ "ติดต่อพยาบาล/แพทย์" อย่างเดียว → ข้าม ไม่แสดง
   - ถ้าไม่มีคำแนะนำสำหรับอาการนี้ใน context → ข้าม ไม่แสดง
7. **ตัวอย่างที่ถูกต้อง:**
   • เลือดออก: กัดผ้าก๊อซให้แน่นหากเลือดออกในช่องปาก หรือก้มหน้าและกดปีกจมูกเข้ากันหากเลือดออกจากจมูก ร่วมกับประคบเย็นนอกช่องปาก
   • อาการไข้: เช็ดตัว ทานยาลดไข้ พาราเซตามอล
   • ลวดมัดฟัน: ติดต่อพยาบาลเพื่อทำการนัดหมายกับทันตแพทย์ทันที

"""
    return base_prompt


def build_low_risk_prompt(
    name_text: str,
    all_risk_items: List[str],
    recommendations_context: str,
    language: str = 'th'
) -> str:
    """สร้าง prompt สำหรับกรณีเสี่ยงต่ำ"""
    
    if language == 'en':
        return f"""You are a nurse communicating with a patient via LINE using English.

SYMPTOM DETAILS:
{chr(10).join(f'{i+1}. {item}' for i, item in enumerate(all_risk_items)) if all_risk_items else '- None'}
{recommendations_context}

TASK: Generate a message following the FORMAT below strictly.

**REQUIRED FORMAT:**

Based on the assessment, the risk of post-operative complications is LOW.
Overall symptoms are normal.

Preliminary recommendations based on symptoms
[Short Topic 3-5 words]: [Full recommendation from context]
[Short Topic 3-5 words]: [Full recommendation from context]

If you have questions, call {PHONE_NUMBER}

**STRICT RULES:**

0. **CRITICAL: Use ONLY recommendations from "Rule-based Assessment Recommendations:" section above.** 
   - DO NOT create, invent, or generate any new recommendations.
   - If a symptom has NO recommendation in the context -> SKIP IT COMPLETELY.
   - Copy recommendations EXACTLY as written - word for word.
   
1. **If "Rule-based Assessment Recommendations: No specific recommendations." OR if there are NO recommendations listed:**
   - Remove the entire "Preliminary recommendations based on symptoms:" section.
   - Keep only: risk statement + phone contact line.
   
2. **NO markdown** (**, *, •, #) and **NO emojis**.
3. Use Plain Text only.
4. **NO PARENTHESES ()** in any part.
5. **NO bullet points (•)** - Use "Topic: Recommendation" format only.
6. **Symptom Topics:**
   - Short 3-5 words only.
   - NO "Other symptoms".
   - Good: "Numbness", "Brushing", "Rinsing"
   - Bad: "Numbness (at lips)", "Other symptoms"
7. **Recommendations:**
   - Copy full recommendation from context.
   - Remove "See doctor", "Contact nurse".
   - If recommendation is ONLY "Contact nurse/doctor" -> Skip.
   - If NO recommendation exists for this symptom in context -> Skip.
8. **Correct Examples:**
   Numbness: Observe symptoms, if numbness lasts over 2 weeks, see dentist
   Brushing: Use small soft brush + non-stinging toothpaste, brush gently avoiding wound
   Rinsing: Rinse gently with water or mouthwash after every meal
"""

    base_prompt = f"""คุณเป็นพยาบาลที่สื่อสารกับผู้ป่วยผ่าน LINE

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

0. **สำคัญมาก: ใช้เฉพาะคำแนะนำจาก "คำแนะนำจาก Rule-based Assessment:" ด้านบนเท่านั้น**
   - ห้ามแต่ง ห้ามสร้าง ห้ามคิดคำแนะนำใหม่ขึ้นมาเอง
   - ถ้าอาการใดไม่มีคำแนะนำใน context → ข้ามอาการนั้นไป ไม่ต้องแสดง
   - คัดลอกคำแนะนำตามที่ให้มาทุกคำ ทุกตัวอักษร
   
1. **กฎการตัดส่วน:**
   - ถ้าไม่มีคำแนะนำเลย (ทุกอาการเป็น "- ไม่มีคำแนะนำ") → ตัดส่วน "คำแนะนำเบื้องต้นตามอาการ:" ทั้งหมดออก
   - เหลือแค่: ข้อความอาการต่ำ + บรรทัดติดต่อโทรศัพท์
   
2. **ห้ามใช้ markdown** (**, *, •, #) และ **ห้ามใช้ emoji** ทุกชนิด
3. ใช้ข้อความ plain text เท่านั้น
4. **ห้ามใส่วงเล็บ ()** ในทุกส่วน - ห้ามใส่คำอธิบายหรืออาการในวงเล็บ
5. **ห้ามใช้ bullet point (•)** - ใช้รูปแบบ "หัวข้อ: คำแนะนำ" เท่านั้น
6. **หัวข้ออาการ:**
   - ย่อให้สั้น 3-5 คำเท่านั้น จับคีย์เวิร์ดสำคัญ
   - ห้ามใช้ "อาการอื่นๆ" - ต้องระบุอาการชัดเจน
   - ตัวอย่างที่ถูก: "อาการชา", "การแปรงฟัน", "การบ้วนปาก"
   - ตัวอย่างที่ผิด: "อาการชา (บริเวณริมฝีปาก)", "อาการอื่นๆ"
7. **คำแนะนำ:**
   - คัดลอกคำแนะนำเต็มจาก recommendations_context ทุกคำ
   - ห้ามขึ้นต้นด้วย "แนะนำ" - เริ่มจากการกระทำเลย
   - ตัดคำว่า "พบแพทย์", "พบพยาบาล", "ติดต่อแพทย์", "ติดต่อพยาบาล" ออก
   - ถ้าคำแนะนำมีแค่ "ติดต่อพยาบาล/แพทย์" อย่างเดียว → ข้าม ไม่แสดง
   - ถ้าไม่มีคำแนะนำสำหรับอาการนี้ใน context → ข้าม ไม่แสดง
8. **ตัวอย่างที่ถูกต้อง:**
   อาการชา: สังเกตอาการ หากชานานเกิน 2 สัปดาห์ ควรพบทันตแพทย์
   การแปรงฟัน: ใช้แปรงหัวเล็กขนนุ่ม + ยาสีฟันไม่แสบ แปรงเบาๆ หลีกเลี่ยงเหงือกที่มีแผล
   การบ้วนปาก: บ้วนปากเบาๆด้วยน้ำเปล่าหรือน้ำยาบ้วนปาก ทุกครั้งหลังทานอาหาร
"""
    return base_prompt


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

**Important Rules:**
1. **Very short answer** - Start with direct answer.
2. **No formal address** like "Sir/Madam" (Friendly LINE style).
3. If urgent: Use "Inform dentist immediately" (No long explanation).
4. If not urgent: Answer directly with short advice.

Examples:
- Q: "Hard to breathe, what should I do?"
- A: "This is urgent. Inform dentist immediately."

- Q: "How long to compress?"
- A: "Compress 15-20 mins, 3-4 times a day, especially after meals."

- Q: "When will numbness go away?"
- A: "Usually improves in 2-3 weeks. If not, please inform dentist."

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
    return prompt
