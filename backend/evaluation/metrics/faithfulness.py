"""
Faithfulness Metric - ตรวจสอบว่า LLM output ตรงกับข้อมูลต้นทางหรือไม่ (ไม่หลอน)
ใช้ QAG (Question Answer Generation) Scorer ตามแนวทางของ Confident AI
"""
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
import json
import re


class FaithfulnessMetric(BaseMetric):
    """
    วัดความ faithful ของ summary โดยใช้ QAG approach:
    1. แยกคำกล่าวอ้าง (claims) จาก actual output
    2. ตรวจสอบแต่ละ claim ว่าตรงกับข้อมูลต้นทาง
    3. คำนวณสัดส่วนของ claims ที่ truthful
    """
    
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self.score = 0
        self.reason = ""
        self.success = False
        
    def measure(self, test_case: LLMTestCase) -> float:
        """
        QAG-based faithfulness evaluation:
        1. Extract all claims from actual_output
        2. For each claim, verify against input + expected_output
        3. Calculate proportion of truthful claims
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
            max_output_tokens=None,  # No limit - get full response.1,
            max_tokens=8192
        )
        
        # Step 1: Extract claims
        extraction_prompt = f"""
คุณเป็น AI ที่ช่วยแยกคำกล่าวอ้าง (claims) จากข้อความ

ข้อความที่ต้องวิเคราะห์:
{test_case.actual_output}

งาน: แยกทุกคำกล่าวอ้างที่สามารถตรวจสอบได้ ออกเป็นรายการ

ตัวอย่าง:
ข้อความ: "ผู้ป่วยมีอาการปวด 8/10 และมีเลือดออก ควรกัดผ้าก๊อซ 30 นาที"
Claims:
- ผู้ป่วยมีอาการปวด 8/10
- ผู้ป่วยมีเลือดออก
- แนะนำให้กัดผ้าก๊อซ 30 นาที

ให้ตอบในรูปแบบ JSON list:
{{"claims": ["claim1", "claim2", ...]}}
"""
        
        try:
            # Extract claims
            extract_response = llm.invoke(extraction_prompt)
            extract_text = extract_response.content.strip()
            
            # Parse claims
            try:
                json_match = re.search(r'\{.*"claims".*\}', extract_text, re.DOTALL)
                if json_match:
                    claims_data = json.loads(json_match.group())
                    claims = claims_data.get("claims", [])
                else:
                    # Fallback: split by newlines
                    claims = [c.strip('- ').strip() for c in extract_text.split('\n') if c.strip() and c.strip().startswith('-')]
            except:
                claims = [c.strip('- ').strip() for c in extract_text.split('\n') if c.strip() and len(c) > 10]
            
            if not claims:
                self.score = 0.5
                self.reason = "ไม่สามารถแยก claims ได้"
                self.success = self.score >= self.threshold
                return self.score
            
            # Step 2: Verify each claim
            truthful_count = 0
            verification_results = []
            
            # Prepare context data (include retrieval_context if available)
            context_info = test_case.input
            template_context = ""
            if test_case.retrieval_context:
                try:
                    context_data = json.loads(test_case.retrieval_context[0])
                    overall_risk = context_data.get('risk_level', 'ไม่ระบุ')
                    template_phrases = context_data.get('template_phrases', [])
                    
                    context_info += f"\n\nระดับความเสี่ยงรวม: {overall_risk}"
                    
                    # Add template phrases to context
                    if template_phrases:
                        template_context = "\n\nข้อความมาตรฐานตาม Format (ถือว่าเป็นความจริง):\n" + "\n".join(f"- {phrase}" for phrase in template_phrases)
                except:
                    pass
            
            for claim in claims:
                verify_prompt = f"""
ตรวจสอบความจริงของคำกล่าวอ้าง

ข้อมูลอ้างอิง (Input Data + Risk Level):
{context_info}
{template_context}

คำแนะนำที่ควรจะเป็น (Expected):
{test_case.expected_output if test_case.expected_output else "ไม่มีข้อมูล"}

คำกล่าวอ้างที่ต้องตรวจสอบ:
"{claim}"

**หมายเหตุสำคัญ - ห้ามประเมินผิด:**
1. **ข้อความมาตรฐานตาม Format ถือว่าเป็นความจริงเสมอ** (เช่น "มีความเสี่ยง...", "อาการโดยรวมอยู่ในเกณฑ์ปกติ")
2. **"อาการโดยรวมอยู่ในเกณฑ์ปกติ"** = ความเสี่ยงต่ำ (แม้จะมีอาการเล็กน้อย เช่น ปวดนิดหน่อย, ปวดหัว แต่ไม่เสี่ยง)
3. **"ทีมพยาบาลจะติดต่อกลับ"** = template สำหรับความเสี่ยงปานกลาง/ซับซ้อน (เป็นความจริง)

คำถาม: คำกล่าวนี้ตรงกับข้อมูลอ้างอิง (รวมข้อความมาตรฐานตาม Format) หรือไม่?

ตอบ 'yes' ถ้า:
- คำกล่าวตรงกับข้อมูล input (รวมระดับความเสี่ยง)
- คำกล่าวสอดคล้องกับ expected recommendations
- เป็นข้อมูลที่สามารถอนุมานได้จากข้อมูลอ้างอิง
- **เป็นข้อความมาตรฐานตาม Format ที่ระบุไว้**

ตอบ 'no' ถ้า:
- คำกล่าวขัดแย้งกับข้อมูล
- แต่งเรื่องหรือข้อมูลที่ไม่มีในอ้างอิง
- พูดเกินความจริง

ตอบ 'idk' ถ้า:
- ไม่มีข้อมูลเพียงพอในอ้างอิงเพื่อตรวจสอบ

ตอบแค่คำเดียว: yes/no/idk
(ห้ามอธิบายยาว)
"""
                
                verify_response = llm.invoke(verify_prompt)
                answer = verify_response.content.strip().lower()
                
                # Only count 'yes' as truthful, treat 'idk' and 'no' as not truthful
                is_truthful = 'yes' in answer and 'no' not in answer
                if is_truthful:
                    truthful_count += 1
                
                verification_results.append({
                    "claim": claim,
                    "verdict": answer,
                    "truthful": is_truthful
                })
            
            # Step 3: Calculate score
            self.score = truthful_count / len(claims) if claims else 0.0
            self.score = max(0.0, min(1.0, self.score))
            
            # Generate reason with detailed claims
            truthful_claims = [r['claim'] for r in verification_results if r['truthful']]
            false_claims = [r['claim'] for r in verification_results if not r['truthful']]
            
            self.reason = f"Truthful claims: {truthful_count}/{len(claims)} = {self.score:.2f}"
            
            # Add truthful claims list
            if truthful_claims:
                self.reason += f"\n✓ Claims ที่ตรง ({len(truthful_claims)}):\n"
                self.reason += "\n".join(f"  - {claim}" for claim in truthful_claims[:5])  # Show max 5
                if len(truthful_claims) > 5:
                    self.reason += f"\n  ... และอีก {len(truthful_claims) - 5} claims"
            
            # Add false claims list
            if false_claims:
                self.reason += f"\n✗ Claims ที่ไม่ตรง ({len(false_claims)}):\n"
                self.reason += "\n".join(f"  - {claim}" for claim in false_claims[:5])  # Show max 5
                if len(false_claims) > 5:
                    self.reason += f"\n  ... และอีก {len(false_claims) - 5} claims"
            
            self.success = self.score >= self.threshold
            return self.score
            
        except Exception as e:
            print(f"Error in FaithfulnessMetric: {e}")
            self.score = 0.5
            self.reason = f"Error: {str(e)}"
            self.success = False
            return self.score
    
    def is_successful(self) -> bool:
        return self.success
    
    @property
    def __name__(self):
        return "Faithfulness"
