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
    _cached_steps = {}  # Changed to dict to support multiple languages
    _criteria_file_map = {
        "th": "../criteria/th/completeness.txt",
        "en": "../criteria/en/completeness.txt"
    }
    
    def __init__(
        self, 
        threshold: float = 0.7,
        model: str = "deepseek-chat",  # Changed from Gemini to DeepSeek
        include_reason: bool = True,
        language: str = "th"
    ):
        self.threshold = threshold
        self.model = model
        self.include_reason = include_reason
        self.language = language
        self.score = 0
        self.reason = ""
        self.success = False
    
    @classmethod
    def _load_criteria_from_file(cls, language="th"):
        """Load cached criteria from file if exists"""
        import os
        from pathlib import Path
        
        # Get path relative to this file's location
        metrics_dir = Path(__file__).parent
        criteria_file = metrics_dir.parent / "criteria" / language / "completeness.txt"
        
        if criteria_file.exists():
            with open(criteria_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        return None
    
    @classmethod
    def _save_criteria_to_file(cls, criteria, language="th"):
        """Save criteria to file for future use"""
        from pathlib import Path
        
        metrics_dir = Path(__file__).parent
        criteria_file = metrics_dir.parent / "criteria" / language / "completeness.txt"
        
        with open(criteria_file, 'w', encoding='utf-8') as f:
            f.write(criteria)
        
    def measure(self, test_case: LLMTestCase) -> float:
        """Evaluate completeness using DeepSeek (G-Eval approach)"""
        from langchain_openai import ChatOpenAI
        import os
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is required")
        
        llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=api_key,
            base_url="https://api.deepseek.com",
            temperature=0,
            timeout=60,
            max_tokens=None
        )
        
        # Step 1: Generate/Load evaluation steps (cache per language)
        if self.language not in CompletenessMetric._cached_steps:
            cached = CompletenessMetric._load_criteria_from_file(self.language)
            if cached:
                print(f"    📂 Loaded Completeness criteria from file ({self.language})")
                CompletenessMetric._cached_steps[self.language] = cached
            else:
                print(f"    🔧 Generating Completeness criteria (first time, {self.language})...")
                if self.language == "en":
                    step_generation_prompt = """You are creating evaluation steps for "Completeness" assessment of medical recommendation summaries.

Completeness Scoring Criteria (0-10):
10 = Includes all recommendations completely, nothing missing, covers all dimensions
7-9 = Mostly complete, has all important recommendations, may lack minor non-critical details
4-6 = Partially complete, has some main recommendations but missing several important ones
1-3 = Missing many important recommendations, only some parts present
0 = No recommendations at all or everything is missing

Completeness means:
- Important recommendations from rule-based are fully included in summary
- No missing critical recommendations such as care methods, medication instructions, compress methods
- For high/medium risk, must have specific recommendations completely
- For low risk, must have main recommendations even if summarized

Examples:
✅ Complete (10): Includes all recommendations from rule-based, nothing missing
✅ Good (8): Has all main recommendations, may skip minor details
⚠️ Partial (5): Has some recommendations but missing several important ones
❌ Incomplete (2): Missing almost all important recommendations

Please create evaluation steps that:
1. Compare recommendations in summary with rule-based recommendations
2. Check if important recommendations are included
3. Count complete and missing recommendations
4. Consider importance of missing recommendations

Then use those steps with the scoring criteria above to evaluate Completeness."""
                else:
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
                CompletenessMetric._cached_steps[self.language] = steps_response.content.strip()
                CompletenessMetric._save_criteria_to_file(CompletenessMetric._cached_steps[self.language], self.language)
                print("    💾 Saved criteria to file for future use")
        
        evaluation_steps = CompletenessMetric._cached_steps[self.language]
        
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
