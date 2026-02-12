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
    _cached_steps = {}  # Changed to dict to support multiple languages
    _criteria_file_map = {
        "th": "../criteria/th/conciseness.txt",
        "en": "../criteria/en/conciseness.txt"
    }
    
    def __init__(self, threshold: float = 0.7, language: str = "th"):
        self.threshold = threshold
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
        criteria_file = metrics_dir.parent / "criteria" / language / "conciseness.txt"
        
        if criteria_file.exists():
            with open(criteria_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        return None
    
    @classmethod
    def _save_criteria_to_file(cls, criteria, language="th"):
        """Save criteria to file for future use"""
        from pathlib import Path
        
        metrics_dir = Path(__file__).parent
        criteria_file = metrics_dir.parent / "criteria" / language / "conciseness.txt"
        
        with open(criteria_file, 'w', encoding='utf-8') as f:
            f.write(criteria)
        
    def measure(self, test_case: LLMTestCase) -> float:
        """
        G-Eval based conciseness evaluation:
        1. Generate evaluation steps via CoT
        2. Use steps to determine score 1-5
        3. Normalize to 0-1 scale
        """
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
        
        # Step 1: Generate evaluation steps with scoring criteria (G-Eval CoT)
        if self.language == "en":
            step_generation_prompt = f"""
You are creating evaluation steps for "Conciseness" assessment of medical recommendation summaries.

Conciseness Scoring Criteria (1-5):
5 = Very Concise: No redundancy at all, appropriate length for content, every word has meaning
4 = Good Conciseness: Minor words could be reduced but doesn't affect clarity
3 = Acceptable: Some redundancy or slightly excessive length
2 = Not Very Concise: Clear redundancy at multiple points or obviously excessive length
1 = Not Concise At All: Extensive redundancy or extremely excessive length, inefficient

Conciseness means:
- Text is reasonably concise, not overly verbose
- Words that add clarity (e.g., "in the mouth", "as needed") are not considered filler
- Information is combined efficiently
- No truly unnecessary repeated words or phrases

Examples:
✅ Concise (5): "Bite gauze 30 minutes, if not stopped see doctor" (short, clear, no repetition)
⚠️ Redundant (2): "Bite gauze, bite firmly, bite for 30 minutes" (repeats "bite")
❌ Too Long (1): "You should perform the action of biting gauze firmly for approximately 30 minutes in order to help the bleeding stop" (overly verbose)

Please create evaluation steps that:
1. Check for redundancy
2. Check length vs content
3. Check communication efficiency
4. Check for unnecessary words

Then use those steps with the scoring criteria above to evaluate Conciseness.
"""
        else:
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
            # Load or generate evaluation steps (once per language, then cache)
            if self.language not in ConcisenessMetric._cached_steps:
                # Try loading from file first
                cached = ConcisenessMetric._load_criteria_from_file(self.language)
                if cached:
                    print(f"    📂 Loaded Conciseness criteria from file ({self.language})")
                    ConcisenessMetric._cached_steps[self.language] = cached
                else:
                    # Generate new criteria
                    print(f"    🔧 Generating Conciseness criteria (first time, {self.language})...")
                    steps_response = llm.invoke(step_generation_prompt)
                    ConcisenessMetric._cached_steps[self.language] = steps_response.content.strip()
                    # Save to file
                    ConcisenessMetric._save_criteria_to_file(ConcisenessMetric._cached_steps[self.language], self.language)
                    print("    💾 Saved criteria to file for future use")
            
            evaluation_steps = ConcisenessMetric._cached_steps[self.language]
            
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
