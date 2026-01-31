"""
Conciseness Metric - ตรวจสอบความกระชับ (ไม่ยาว ไม่ซ้ำซาก)
ใช้ G-Eval framework ตามแนวทางของ Confident AI
"""
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
import re


class ConcisenessMetric(BaseMetric):
    """
    วัดความกระชับของ summary โดยใช้ G-Eval:
    1. Generate evaluation steps via chain-of-thought
    2. Use steps to determine score from 1-5
    3. Normalize to 0-1 scale
    """
    
    # Class-level cache for evaluation steps (shared across all instances)
    _cached_steps = None
    _criteria_file = "evaluation_criteria_conciseness.txt"
    
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
        G-Eval based conciseness evaluation:
        1. Generate evaluation steps via CoT
        2. Use steps to determine score 1-5
        3. Normalize to 0-1 scale
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
        
        # Step 1: Generate evaluation steps with scoring criteria (G-Eval CoT)
        step_generation_prompt = f"""
คุณกำลังสร้างขั้นตอนการประเมิน "Conciseness" (ความกระชับ) สำหรับสรุปคำแนะนำทางการแพทย์

เกณฑ์คะแนน Conciseness (1-5):
5 = กระชับมาก ไม่ซ้ำซ้อนเลย ความยาวเหมาะสมกับเนื้อหา แต่ละคำมีความหมาย
4 = กระชับดี มีคำที่อาจลดได้เล็กน้อย แต่ไม่กระทบความชัดเจน
3 = พอใช้ มีความซ้ำซ้อนบ้าง หรือยาวเกินความจำเป็นเล็กน้อย
2 = ไม่ค่อยกระชับ ซ้ำซ้อนชัดเจนหลายจุด หรือยาวเกินไปชัดเจน
1 = ไม่กระชับเลย ซ้ำซ้อนมาก หรือยาวมากเกินไป ไม่มีประสิทธิภาพ

Conciseness หมายถึง:
- ข้อความกระชับพอสมควร ไม่ยืดยาดเกินไป
- คำที่เพิ่มความชัดเจน (เช่น "ในช่องปาก", "ตามอาการ") ไม่ถือว่าฟุ่มเฟือย
- ข้อมูลรวมกันอย่างมีประสิทธิภาพ
- ไม่มีคำหรือประโยคที่ซ้ำซากจริงๆ โดยไม่จำเป็น

ตัวอย่าง:
✅ กระชับ (5): "กัดผ้าก๊อซ 30 นาที ถ้าไม่หยุดพบแพทย์" (สั้น ชัดเจน ไม่ซ้ำ)
⚠️ ซ้ำซ้อน (2): "กัดผ้าก๊อซ กัดให้แน่น กัดนาน 30 นาที" (ซ้ำคำ "กัด")
❌ ยาวเกิน (1): "ควรทำการกัดผ้าก๊อซอย่างแน่นหนาเป็นเวลานานประมาณ 30 นาทีเพื่อที่จะช่วยให้เลือดหยุด" (ยืดยาดเกินไป)

กรุณาสร้างขั้นตอนการประเมิน (evaluation steps) ที่:
1. ตรวจสอบความซ้ำซ้อน (Redundancy)
2. ตรวจสอบความยาวเทียบกับเนื้อหา (Length vs Content)
3. ตรวจสอบประสิทธิภาพการสื่อสาร (Communication Efficiency)
4. ตรวจสอบคำที่ไม่จำเป็น (Unnecessary Words)

แล้วใช้ขั้นตอนนั้นกับเกณฑ์คะแนนข้างต้นเพื่อประเมิน Conciseness
"""
        
        try:
            # Load or generate evaluation steps (once, then cache)
            if ConcisenessMetric._cached_steps is None:
                # Try loading from file first
                cached = ConcisenessMetric._load_criteria_from_file()
                if cached:
                    print("    📂 Loaded Conciseness criteria from file")
                    ConcisenessMetric._cached_steps = cached
                else:
                    # Generate new criteria
                    print("    🔧 Generating Conciseness criteria (first time)...")
                    steps_response = llm.invoke(step_generation_prompt)
                    ConcisenessMetric._cached_steps = steps_response.content.strip()
                    # Save to file
                    ConcisenessMetric._save_criteria_to_file(ConcisenessMetric._cached_steps)
                    print("    💾 Saved criteria to file for future use")
            
            evaluation_steps = ConcisenessMetric._cached_steps
            
            # นับจำนวนประโยค
            sentences = [s.strip() for s in test_case.actual_output.split('\n') if s.strip()]
            n_sentences = len(sentences)
            
            # Step 2: Use generated steps with criteria to evaluate (G-Eval scoring)
            scoring_prompt = f"""
ใช้ขั้นตอนการประเมินต่อไปนี้:

{evaluation_steps}

เกณฑ์คะแนน Conciseness (1-5):
5 = กระชับมาก ไม่ซ้ำซ้อนเลย ความยาวเหมาะสมกับเนื้อหา แต่ละคำมีความหมาย
4 = กระชับดี มีเล็กน้อยที่อาจรวมได้ ส่วนใหญ่เหมาะสม
3 = พอใช้ มีความซ้ำซ้อนบ้าง หรือยาวเกินความจำเป็น
2 = ไม่ค่อยกระชับ ซ้ำซ้อนหลายจุด หรือยาวเกินไปชัดเจน
1 = ไม่กระชับเลย ซ้ำซ้อนมาก หรือยาวมากเกินไป ไม่มีประสิทธิภาพ

ข้อความที่ต้องประเมิน:
{test_case.actual_output}

จำนวนประโยค: {n_sentences}

**หลักการประเมิน - ห้ามฝ่าฝืน (CRITICAL):**

1. ** หักเฉพาะที่ซ้ำซ้อนมากจริงๆ

2. **คำที่มาจาก template ห้ามหักโดยเด็ดขาด:**
   - "คุณผู้ป่วย", "จากการประเมิน พบว่า" = template (ห้ามหัก)
   - "แนะนำให้", "ควร", "มีความเสี่ยงต่อการเกิด" = template (ห้ามหัก)
   - "ในระดับสูง/ปานกลาง/ต่ำ" = บอกระดับ (ห้ามหัก)

3. **คำศัพท์ทางการแพทย์ห้ามหัก:**
   - "อาการ" = คำศัพท์ทางการแพทย์ (ห้ามหัก)
   - "อาการปวด", "อาการบวม", "อาการเลือดออก" = ถูกต้อง (ห้ามหัก)

4. **คำที่เพิ่มความหมายห้ามหัก:**
   - "มาก", "เล็กน้อย", "ปานกลาง" = บอกระดับ (ห้ามหัก)
   - "อาการปวดมากในระดับ 9" = ถูกต้อง (ห้ามหัก)
   - "ในช่องปาก", "นอกช่องปาก" = บอกตำแหน่ง (ห้ามหัก)

5. **คำเชื่อมและคำบอกทิศทางห้ามหัก:**
   - "ร่วมกับ", "และ", "หรือ", "เนื่องจาก" = จำเป็น (ห้ามหัก)
   - "ตามอาการ", "ตามที่แพทย์สั่ง", "เบื้องต้น" = จำเป็น (ห้ามหัก)

6. **หักคะแนนเฉพาะ:**
   - ซ้ำคำเดียวกัน 4+ ครั้งในประโยคเดียว
   - ขยายความซ้ำซ้อนมาก (เช่น "แนะนำให้ทำ และควรทำ และแนะนำว่าทำ")

งาน: ใช้ขั้นตอนและเกณฑ์คะแนนข้างต้น ประเมิน Conciseness ของข้อความ

ให้คะแนนและอธิบายเหตุผลแบบสั้นมาก (1-2 ประโยค เท่านั้น)

รูปแบบ (ห้ามยาว):
เหตุผล: [สรุปสั้นๆ 1-2 ประโยค]
คะแนน: [1-5]
"""
            
            score_response = llm.invoke(scoring_prompt)
            score_text = score_response.content.strip()
            
            # Extract score (1-5)
            score_match = re.search(r'คะแนน[:\s]+([1-5])', score_text)
            if score_match:
                raw_score = int(score_match.group(1))
                # Normalize to 0-1 scale
                self.score = (raw_score - 1) / 4.0
            else:
                # Fallback: parse any number
                numbers = re.findall(r'[1-5]', score_text)
                if numbers:
                    raw_score = int(numbers[-1])  # Take last number
                    self.score = (raw_score - 1) / 4.0
                else:
                    # Fallback based on sentence count
                    if n_sentences <= 6:
                        self.score = 0.9
                    elif n_sentences <= 8:
                        self.score = 0.7
                    elif n_sentences <= 10:
                        self.score = 0.5
                    else:
                        self.score = 0.3
            
            # Extract reason
            reason_match = re.search(r'เหตุผล[:\s]+(.+?)(?=คะแนน|$)', score_text, re.DOTALL)
            if reason_match:
                self.reason = reason_match.group(1).strip()
            else:
                self.reason = f"จำนวนประโยค: {n_sentences}, Score: {self.score:.2f}"
            
            self.score = max(0.0, min(1.0, self.score))
            self.success = self.score >= self.threshold
            return self.score
            
        except Exception as e:
            print(f"Error in ConcisenessMetric: {e}")
            # Fallback based on sentence count
            n_sentences = len([s for s in test_case.actual_output.split('\n') if s.strip()])
            if n_sentences <= 6:
                self.score = 0.8
            elif n_sentences <= 8:
                self.score = 0.6
            else:
                self.score = 0.4
            self.success = self.score >= self.threshold
            return self.score
    
    def is_successful(self) -> bool:
        return self.success
    
    @property
    def __name__(self):
        return "Conciseness"
