"""
Completeness Metric - วัดความครบถ้วนของคำแนะนำโดยใช้ LLM-as-a-Judge
ใช้ G-Eval framework แบบ Gemini-based เพื่อประเมินว่า:
LLM summary รวมคำแนะนำจาก rule-based engine ครบถ้วนหรือไม่
"""
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
import json
import re


class CompletenessMetric(BaseMetric):
    """
    วัดความครบถ้วนของคำแนะนำโดยใช้ LLM-as-a-Judge (Gemini-based G-Eval)
    
    ตรวจสอบว่า:
    1. คำแนะนำจาก rule-based ถูกนำมาใส่ใน summary ครบหรือไม่
    2. อาการสำคัญ (เสี่ยงสูง/กลาง) ไม่ถูกข้ามไป
    3. คำแนะนำเป็นไปตามระดับความเสี่ยง
    
    """
    
    # Class-level cache for evaluation steps
    _cached_steps = None
    _criteria_file = "evaluation_criteria_completeness.txt"
    
    def __init__(
        self, 
        threshold: float = 0.7,
        model: str = "gemini-2.0-flash",  # Changed from gpt-4o-mini to Gemini
        include_reason: bool = True
    ):
        self.threshold = threshold
        self.model = model
        self.include_reason = include_reason
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
        """Evaluate completeness using Gemini (G-Eval approach)"""
        from langchain_google_genai import ChatGoogleGenerativeAI
        import os
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        llm = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=api_key,
            temperature=0,
            timeout=60,
            max_output_tokens=None  # No limit - get full response
        )
        
        # Step 1: Generate/Load evaluation steps (cache)
        if CompletenessMetric._cached_steps is None:
            cached = CompletenessMetric._load_criteria_from_file()
            if cached:
                print("    📂 Loaded Completeness criteria from file")
                CompletenessMetric._cached_steps = cached
            else:
                print("    🔧 Generating Completeness criteria (first time)...")
                step_generation_prompt = """คุณกำลังสร้างขั้นตอนการประเมิน "Completeness" (ความครบถ้วน) สำหรับสรุปคำแนะนำทางการแพทย์

เกณฑ์คะแนน Completeness (0-10):
10 = รวมคำแนะนำครบถ้วนทุกข้อ ไม่ขาดอะไรเลย ครอบคลุมทุกมิติ
7-9 = ครบส่วนใหญ่ มีคำแนะนำสำคัญครบ อาจขาดรายละเอียดเล็กน้อยที่ไม่สำคัญมาก
4-6 = ครบบางส่วน มีคำแนะนำหลักบ้าง แต่ขาดคำแนะนำสำคัญหลายข้อ
1-3 = ขาดคำแนะนำสำคัญหลายข้อ มีเพียงบางส่วนเท่านั้น
0 = ไม่มีคำแนะนำเลย หรือขาดหมดทุกอย่าง

Completeness หมายถึง:
- คำแนะนำสำคัญจาก rule-based ถูกรวมอยู่ใน summary ครบถ้วน
- ไม่ขาดคำแนะนำสำคัญ เช่น วิธีดูแล วิธีทานยา วิธีประคบ
- สำหรับเสี่ยงสูง/กลาง ต้องมีคำแนะนำเฉพาะเจาะจงครบถ้วน
- สำหรับเสี่ยงต่ำ ต้องมีคำแนะนำหลักๆ แม้จะสรุปได้

ตัวอย่าง:
✅ ครบถ้วน (10): รวมทุกคำแนะนำจาก rule-based ไม่ขาด ไม่ตก
✅ ครบดี (8): มีคำแนะนำหลักครบ อาจข้ามรายละเอียดเล็กน้อย
⚠️ ครบบางส่วน (5): มีบางคำแนะนำ แต่ขาดหลายข้อสำคัญ
❌ ไม่ครบ (2): ขาดคำแนะนำสำคัญเกือบทั้งหมด

กรุณาสร้างขั้นตอนการประเมิน (evaluation steps) ที่:
1. เปรียบเทียบคำแนะนำใน summary กับ rule-based recommendations
2. ตรวจสอบว่าคำแนะนำสำคัญถูกรวมไว้หรือไม่
3. นับจำนวนคำแนะนำที่ครบและขาด
4. พิจารณาความสำคัญของคำแนะนำที่ขาดไป

แล้วใช้ขั้นตอนนั้นกับเกณฑ์คะแนนข้างต้นเพื่อประเมิน Completeness"""
                steps_response = llm.invoke(step_generation_prompt)
                CompletenessMetric._cached_steps = steps_response.content.strip()
                CompletenessMetric._save_criteria_to_file(CompletenessMetric._cached_steps)
                print("    💾 Saved criteria to file for future use")
        
        evaluation_steps = CompletenessMetric._cached_steps
        
        # Parse retrieval_context to extract recommendations
        context_str = ""
        if test_case.retrieval_context:
            try:
                context_data = json.loads(test_case.retrieval_context[0])
                flows = context_data.get('flows', {})
                recommendations = []
                for flow_name, flow_data in flows.items():
                    rec = flow_data.get('recommendation', '')
                    if rec and rec.strip():
                        recommendations.append(f"{flow_name}: {rec}")
                context_str = "\n".join(recommendations)
            except:
                context_str = str(test_case.retrieval_context)
        
        # Step 2: Evaluate using generated steps with criteria
        try:
            scoring_prompt = f"""ใช้ขั้นตอนการประเมินต่อไปนี้:

{evaluation_steps}

เกณฑ์คะแนน Completeness (0-10):
10 = รวมคำแนะนำครบถ้วนทุกข้อ ไม่ขาดอะไรเลย ครอบคลุมทุกมิติ
8-9 = ครบส่วนใหญ่ มีคำแนะนำสำคัญครบ อาจขาดรายละเอียดเล็กน้อยที่ไม่สำคัญมาก
5-7 = ครบบางส่วน มีคำแนะนำหลักบ้าง แต่ขาดคำแนะนำสำคัญหลายข้อ
1-4 = ขาดคำแนะนำสำคัญหลายข้อ มีเพียงบางส่วนเท่านั้น
0 = ไม่มีคำแนะนำเลย หรือขาดหมดทุกอย่าง

คำแนะนำจาก rule-based (retrieval_context):
{context_str}

สรุปจาก LLM (actual_output):
{test_case.actual_output}

งาน: ใช้ขั้นตอนและเกณฑ์คะแนนข้างต้น ประเมิน Completeness โดยเปรียบเทียบว่าครบหรือขาดอะไร

**หลักการประเมิน (สำคัญมาก):**
1. **ประเมินตามความหมายและเจตนา ไม่ใช่ตัวอักษร:**
   - "ติดต่อพยาบาล" = "ติดต่อทันตแพทย์" = "กลับมาพบทันตแพทย์" = "ควรติดต่อทันตแพทย์เพื่อประเมิน"
   - "แนะนำให้ติดต่อ" = "ควรติดต่อ" (เจตนาเดียวกัน)
   - "ทานยาแก้ปวด" = "ทานยาแก้ปวดตามที่แพทย์สั่ง" (ครอบคลุมกัน)

2. **คำแนะนำที่ครอบคลุมกันถือว่าครบ:**
   - หากแนะนำ "ติดต่อพยาบาล" ครอบคลุม "ประเมินอาการปวด" + "ติดต่อทันตแพทย์" = ถือว่าครบ
   - หากบอก "นอนยกศีรษะสูง" ครอบคลุมทั้ง "นอนยกศีรษะสูง 30 องศา" = ถือว่าครบ

3. **คำแนะนำเสี่ยงต่ำที่ไม่มีไม่ถือเป็นการขาดร้ายแรง:**
   - เช่น "ไหมแน่นดี" ไม่ต้องมีคำแนะนำ = ไม่หักคะแนน
   - เช่น "ไม่มีไข้" ไม่ต้องมีคำแนะนำ = ไม่หักคะแนน

4. **ห้ามเข้มงวดเกินไป:**
   - ถ้าคำแนะนำหลักๆ ครบแล้ว แม้จะไม่ได้ละเอียดทุกคำก็ให้ 9-10 คะแนน
   - ห้ามหักคะแนนเพราะคำที่ใช้ต่างกัน แต่ความหมายเดียวกัน

รูปแบบ (ห้ามยาว):
เหตุผล: [อธิบายสั้นๆ 1-2 ประโยค ว่าครบหรือขาดอะไร]
คะแนน: [0-10]"""
            
            score_response = llm.invoke(scoring_prompt)
            score_text = score_response.content.strip()
            
            # Extract score (0-10)
            score_match = re.search(r'คะแนน[:\s]+(\d+)', score_text)
            if score_match:
                raw_score = int(score_match.group(1))
                self.score = min(10, max(0, raw_score)) / 10.0
            else:
                # Fallback
                numbers = re.findall(r'\d+', score_text)
                if numbers:
                    raw_score = int(numbers[-1])
                    self.score = min(10, max(0, raw_score)) / 10.0
                else:
                    self.score = 0.5
            
            # Extract reason
            reason_match = re.search(r'เหตุผล[:\s]+(.+?)(?=คะแนน|$)', score_text, re.DOTALL)
            if reason_match:
                self.reason = reason_match.group(1).strip()
            else:
                self.reason = f"Score: {self.score:.2f}"
            
            self.score = max(0.0, min(1.0, self.score))
            self.success = self.score >= self.threshold
            return self.score
            
        except Exception as e:
            print(f"Error in CompletenessMetric: {e}")
            self.score = 0.5
            self.reason = f"Error: {str(e)[:100]}"
            self.success = self.score >= self.threshold
            return self.score
    
    def is_successful(self) -> bool:
        return self.success
    
    @property
    def __name__(self):
        return "Completeness"
        """Return whether the test was successful"""
        return self.success
    
    @property
    def __name__(self):
        return "Completeness"
