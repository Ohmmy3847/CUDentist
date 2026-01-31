"""
Helpfulness Metric - ตรวจสอบว่าคำแนะนำช่วยเหลือผู้ป่วยได้จริงหรือไม่
Custom metric using G-Eval approach from Confident AI guide
"""
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
import re


class HelpfulnessMetric(BaseMetric):
    """
    วัดความเป็นประโยชน์ของคำแนะนำ:
    - ช่วยผู้ป่วยเข้าใจและจัดการกับอาการ
    - มีขั้นตอนชัดเจน ทำตามได้ง่าย
    - ให้ข้อมูลที่จำเป็นและเพียงพอ
    - ช่วยลดความกังวลและเพิ่มความมั่นใจ
    """
    
    # Class-level cache for evaluation steps (shared across all instances)
    _cached_steps = None
    _criteria_file = "evaluation_criteria_helpfulness.txt"
    
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self.score = 0
        self.reason = ""
        self.success = False
        
    @classmethod
    def _load_criteria_from_file(cls):
        """Load cached criteria from file if exists"""
        import os
        if os.path.exists(cls._criteria_file):
            with open(cls._criteria_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        return None
    
    @classmethod
    def _save_criteria_to_file(cls, criteria):
        """Save criteria to file for future use"""
        with open(cls._criteria_file, 'w', encoding='utf-8') as f:
            f.write(criteria)
        
    def measure(self, test_case: LLMTestCase) -> float:
        """
        G-Eval based helpfulness evaluation:
        1. Generate evaluation steps via CoT
        2. Assess actionability, clarity, completeness
        3. Calculate score
        """
        from langchain_google_genai import ChatGoogleGenerativeAI
        import os
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0,
            timeout=60,
            max_output_tokens=None  # No limit - get full response
        )
        
        # G-Eval: Step 1 - Generate evaluation steps with scoring criteria (CoT)
        steps_prompt = f"""
คุณกำลังสร้างแนวทางการประเมิน "Helpfulness" สำหรับคำแนะนำทางการแพทย์

เกณฑ์คะแนน Helpfulness (1-5):
5 = เป็นประโยชน์มาก ครบถ้วน ชัดเจน ทำตามได้ง่าย
4 = เป็นประโยชน์ดี คำแนะนำชัดเจน ครอบคลุมเนื้อหาสำคัญ
3 = พอใช้ มีประโยชน์บ้าง แต่ขาดรายละเอียดที่สำคัญหลายอย่าง
2 = ไม่ค่อยช่วย ไม่ชัดเจน หรือไม่ครบถ้วน ทำตามยาก
1 = ไม่เป็นประโยชน์เลย ไม่ช่วยผู้ป่วย หรือคลุมเครือมาก

Helpfulness หมายถึง:
- ช่วยให้ผู้ป่วยเข้าใจและสามารถดำเนินการได้จริง (Actionable)
- ให้ข้อมูลที่จำเป็นสำหรับผู้ป่วยทั่วไป (Complete for general patient)
- มีความชัดเจนเพียงพอ (Clear enough)

**หลักการประเมิน - CRITICAL (ห้ามฝ่าฝืน):**

1. ** คำแนะนำที่ชัดเจนและทำตามได้ = ดีแล้ว

2. **ห้ามคาดหวัง "รายละเอียดปลีกย่อย" - นี่ไม่ใช่ข้อผิด:**
   - "ทานยาแก้ปวดตามแพทย์สั่ง" = สมบูรณ์แล้ว ✓ (ไม่ต้องระบุปริมาณ/เวลา)
   - "นอนยกศีรษะสูง" = สมบูรณ์แล้ว ✓ (ไม่ต้องระบุองศา/ชั่วโมง)
   - "ประคบเย็น" = สมบูรณ์แล้ว ✓ (ไม่ต้องระบุนาที/ครั้ง)
   - "กัดผ้าก๊อซให้แน่น" = สมบูรณ์แล้ว ✓ (ไม่ต้องระบุกี่นาที)

3. **ตำแหน่งที่ระบุแล้ว = ชัดเจนสมบูรณ์:**
   - "ประคบเย็นนอกช่องปาก" = สมบูรณ์ ✓ (ไม่ต้องเพิ่ม "แก้ม ริมฝีปาก")
   - "กัดผ้าก๊อซ" = สมบูรณ์ ✓ (เข้าใจว่าในปาก)
   - "นอนยกศีรษะ" = สมบูรณ์ ✓

4. **คำแนะนำเหล่านี้ = 4-5 คะแนน (ไม่ใช่ 0.75):**
   - ✓ "กัดผ้าก๊อซให้แน่น ร่วมกับประคบเย็น"
   - ✓ "นอนยกศีรษะสูง 30 องศา"
   - ✓ "ประคบเย็นนอกช่องปากและนอนยกศีรษะสูง"
   - ✓ "ควรติดต่อทันตแพทย์เพื่อประเมินและปรับแผนการรักษา"
   - ✓ "ตะแคงหน้าไปด้านใดด้านหนึ่งเพื่อป้องกันการสำลัก"

5. **หักคะแนนเฉพาะ:**
   - คลุมเครือมาก (เช่น "ดูแลตัวเองดีดี" "ระวังตัว")
   - ขาดคำแนะนำสำคัญหลายข้อจริงๆ

6. **ห้ามบอกว่า "ขาดรายละเอียดปลีกย่อย" - นี่ไม่ใช่เหตุผลให้หักคะแนน**
- ช่วยลดความกังวลและเพิ่มความมั่นใจ (Reassuring)


แล้วใช้ขั้นตอนนั้นกับเกณฑ์คะแนนข้างต้นเพื่อประเมินคำแนะนำทางการแพทย์
"""
        
        try:
            # Load or generate evaluation steps (once, then cache)
            if HelpfulnessMetric._cached_steps is None:
                # Try loading from file first
                cached = HelpfulnessMetric._load_criteria_from_file()
                if cached:
                    print("    📂 Loaded Helpfulness criteria from file")
                    HelpfulnessMetric._cached_steps = cached
                else:
                    # Generate new criteria
                    print("    🔧 Generating Helpfulness criteria (first time)...")
                    steps_response = llm.invoke(steps_prompt)
                    HelpfulnessMetric._cached_steps = steps_response.content.strip()
                    # Save to file
                    HelpfulnessMetric._save_criteria_to_file(HelpfulnessMetric._cached_steps)
                    print("    💾 Saved criteria to file for future use")
            
            evaluation_steps = HelpfulnessMetric._cached_steps
            
            # G-Eval: Step 2 - Use generated steps with criteria to evaluate
            scoring_prompt = f"""
ใช้ขั้นตอนการประเมินต่อไปนี้:

{evaluation_steps}

เกณฑ์คะแนน Helpfulness (1-5):
5 = เป็นประโยชน์มาก ครบถ้วน ชัดเจน ทำตามได้ง่าย มีรายละเอียดเฉพาะเจาะจง
4 = เป็นประโยชน์ดี มีเล็กน้อยที่ต้องปรับปรุง ส่วนใหญ่ชัดเจน
3 = พอใช้ มีประโยชน์บ้าง แต่ยังขาดรายละเอียดหลายอย่าง
2 = ไม่ค่อยช่วย ไม่ชัดเจน หรือไม่ครบถ้วน ทำตามยาก
1 = ไม่เป็นประโยชน์เลย ไม่ช่วยผู้ป่วย หรือคลุมเครือมาก

อาการและข้อมูลผู้ป่วย:
{test_case.input}

สรุปและคำแนะนำที่ต้องประเมิน:
{test_case.actual_output}

**หลักการประเมิน - อย่าเข้มงวดเกินไป:**
1. **ไม่ต้องคาดหวังรายละเอียดที่แพทย์ต้องกำหนด:**
   - "ทานยาแก้ปวดตามแพทย์สั่ง" = ดีแล้ว (ไม่ต้องระบุปริมาณ)
   - "นอนยกศีรษะสูง" = ดีแล้ว (ไม่ต้องระบุ 30 องศาหรือกี่ชั่วโมง)
   - "ประคบเย็น" = ดีแล้ว (ไม่ต้องระบุกี่นาที)

2. **คำแนะนำที่เฉพาะเจาะจงพอและทำได้ = ให้ 4-5 คะแนน**

3. **หักคะแนนเฉพาะ:**
   - คำแนะนำคลุมเครือมากจริงๆ (เช่น "ดูแลตัวเองดีดี")
   - ขาดคำแนะนำสำคัญหลายข้อ

งาน: ใช้ขั้นตอนและเกณฑ์คะแนนข้างต้น ประเมิน Helpfulness ของคำแนะนำ

**ห้ามเขียนยาว - ตอบสั้นๆ ได้ใจความเท่านั้น (ไม่เกิน 2 ประโยค)**

รูปแบบคำตอบ:
การวิเคราะห์: [สรุปสั้นมาก 1-2 ประโยค ห้ามยาว ห้ามใส่ตัวอย่าง ห้ามใส่ markdown]
คะแนน: [1-5]
"""
            
            score_response = llm.invoke(scoring_prompt)
            score_text = score_response.content.strip()
            
            # Extract score (1-5) and normalize to 0-1
            # Try multiple patterns
            score_match = re.search(r'(?:คะแนน|Score)[:\s]+([1-5])', score_text, re.IGNORECASE)
            if not score_match:
                # Try finding any number 1-5 at end of response
                score_match = re.search(r'([1-5])\s*$', score_text)
            if not score_match:
                # Try finding number after "ให้คะแนน" or similar
                score_match = re.search(r'(?:ให้|คือ|ได้)\s*([1-5])', score_text)
            
            if score_match:
                raw_score = int(score_match.group(1))
                self.score = (raw_score - 1) / 4.0  # Normalize to 0-1
            else:
                # Fallback: find any 1-5 in response
                numbers = re.findall(r'\b([1-5])\b', score_text)
                if numbers:
                    raw_score = int(numbers[-1])  # Use last number found
                    self.score = (raw_score - 1) / 4.0
                else:
                    print(f"    ⚠️ No score found in response, defaulting to 0.5")
                    print(f"    Response: {score_text[:200]}...")
                    self.score = 0.5  # Default to middle score
            
            # Extract analysis - try multiple patterns
            analysis_match = re.search(r'การวิเคราะห์:(.+?)(?=คะแนน|$)', score_text, re.DOTALL)
            if not analysis_match:
                # Try taking everything before "คะแนน:" line
                analysis_match = re.search(r'(.+?)(?=คะแนน|Score)', score_text, re.DOTALL | re.IGNORECASE)
            if not analysis_match:
                # Use full response as reason (no limit)
                self.reason = score_text
            else:
                # Use matched analysis (no limit)
                self.reason = analysis_match.group(1).strip()
            
            self.score = max(0.0, min(1.0, self.score))
            self.success = self.score >= self.threshold
            return self.score
            
        except Exception as e:
            print(f"Error in HelpfulnessMetric: {e}")
            self.score = 0.7
            self.reason = f"Error: {str(e)}"
            self.success = True
            return self.score
    
    def is_successful(self) -> bool:
        return self.success
    
    @property
    def __name__(self):
        return "Helpfulness"
