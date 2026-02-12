"""
Readability Metrics - ตรวจสอบความง่ายในการอ่าน (English only)
ใช้ Flesch Reading Ease (FRE) และ Flesch-Kincaid Grade Level (FKGL)
"""
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
import re
import syllables  # pip install syllables


class ReadabilityMetric(BaseMetric):
    """
    วัดความง่ายในการอ่านของ summary โดยใช้:
    1. Flesch Reading Ease (FRE): คะแนน 0-100 (ยิ่งสูงยิ่งอ่านง่าย)
    2. Flesch-Kincaid Grade Level (FKGL): ระดับการศึกษาที่ต้องใช้
    
    เหมาะสำหรับภาษาอังกฤษเท่านั้น
    
    Medical text ควรมี:
    - FRE ≥ 60 (Standard - Fairly Easy)
    - FKGL ≤ 8 (8th grade level)
    """
    
    def __init__(self, threshold_fre: float = 60.0, threshold_fkgl: float = 8.0):
        """
        Args:
            threshold_fre: คะแนน FRE ขั้นต่ำที่ยอมรับได้ (default: 60 = Standard)
            threshold_fkgl: คะแนน FKGL สูงสุดที่ยอมรับได้ (default: 8 = 8th grade)
        """
        self.threshold_fre = threshold_fre
        self.threshold_fkgl = threshold_fkgl
        self.score = 0
        self.reason = ""
        self.success = False
        
        # Store individual scores
        self.fre_score = 0
        self.fkgl_score = 0
    
    def _count_syllables(self, word: str) -> int:
        """นับพยางค์ในคำ (syllables)"""
        try:
            return syllables.estimate(word)
        except:
            # Fallback: simple estimation
            word = word.lower()
            count = 0
            vowels = "aeiouy"
            previous_was_vowel = False
            
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not previous_was_vowel:
                    count += 1
                previous_was_vowel = is_vowel
            
            # Adjust for silent 'e'
            if word.endswith('e'):
                count -= 1
            
            # Ensure at least 1 syllable
            if count == 0:
                count = 1
                
            return count
    
    def _calculate_readability(self, text: str) -> dict:
        """
        คำนวณ FRE และ FKGL scores
        
        Returns:
            dict: {
                'fre': float,
                'fkgl': float,
                'total_words': int,
                'total_sentences': int,
                'total_syllables': int
            }
        """
        # Remove special characters but keep sentence delimiters
        text = re.sub(r'[^\w\s.!?]', '', text)
        
        # Count sentences (split by . ! ?)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        total_sentences = len(sentences)
        
        if total_sentences == 0:
            return {
                'fre': 0,
                'fkgl': 0,
                'total_words': 0,
                'total_sentences': 0,
                'total_syllables': 0
            }
        
        # Count words
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        total_words = len(words)
        
        if total_words == 0:
            return {
                'fre': 0,
                'fkgl': 0,
                'total_words': 0,
                'total_sentences': total_sentences,
                'total_syllables': 0
            }
        
        # Count syllables
        total_syllables = sum(self._count_syllables(word) for word in words)
        
        # Calculate metrics
        # FRE = 206.835 - 1.015 × (total words / total sentences) - 84.6 × (total syllables / total words)
        fre = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
        
        # FKGL = 0.39 × (total words / total sentences) + 11.8 × (total syllables / total words) - 15.59
        fkgl = 0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words) - 15.59
        
        return {
            'fre': fre,
            'fkgl': fkgl,
            'total_words': total_words,
            'total_sentences': total_sentences,
            'total_syllables': total_syllables
        }
    
    def _interpret_fre(self, score: float) -> str:
        """แปลความหมายคะแนน FRE"""
        if score >= 90:
            return "Very Easy (5th grade)"
        elif score >= 80:
            return "Easy (6th grade)"
        elif score >= 70:
            return "Fairly Easy (7th grade)"
        elif score >= 60:
            return "Standard (8th-9th grade)"
        elif score >= 50:
            return "Fairly Difficult (10th-12th grade)"
        elif score >= 30:
            return "Difficult (College)"
        else:
            return "Very Confusing (College graduate)"
    
    def _interpret_fkgl(self, score: float) -> str:
        """แปลความหมายคะแนน FKGL"""
        grade = int(round(score))
        if grade <= 6:
            return f"Grade {grade} (Easy for most readers)"
        elif grade <= 8:
            return f"Grade {grade} (Appropriate for medical advice)"
        elif grade <= 12:
            return f"Grade {grade} (High school level)"
        else:
            return f"Grade {grade}+ (College level - too complex)"
    
    def measure(self, test_case: LLMTestCase) -> float:
        """
        วัดความง่ายในการอ่านด้วย FRE และ FKGL
        
        Returns:
            float: Combined score 0-1 based on both metrics
        """
        text = test_case.actual_output
        
        # Calculate readability
        stats = self._calculate_readability(text)
        self.fre_score = stats['fre']
        self.fkgl_score = stats['fkgl']
        
        # Check FRE (higher is better, normalize to 0-1)
        # FRE typically ranges 0-100, we want >= threshold_fre
        fre_normalized = min(1.0, max(0.0, self.fre_score / 100.0))
        fre_pass = self.fre_score >= self.threshold_fre
        
        # Check FKGL (lower is better, normalize to 0-1)
        # FKGL typically ranges 0-18, we want <= threshold_fkgl
        fkgl_normalized = max(0.0, 1.0 - (self.fkgl_score / 18.0))
        fkgl_pass = self.fkgl_score <= self.threshold_fkgl
        
        # Combined score (average of both, weighted)
        self.score = (fre_normalized * 0.6 + fkgl_normalized * 0.4)
        
        # Success if both pass thresholds
        self.success = fre_pass and fkgl_pass
        
        # Generate reason
        fre_status = "✓" if fre_pass else "✗"
        fkgl_status = "✓" if fkgl_pass else "✗"
        
        self.reason = f"""Readability Analysis:
{fre_status} FRE Score: {self.fre_score:.1f} / 100 (Target: ≥{self.threshold_fre}) - {self._interpret_fre(self.fre_score)}
{fkgl_status} FKGL Score: {self.fkgl_score:.1f} (Target: ≤{self.threshold_fkgl}) - {self._interpret_fkgl(self.fkgl_score)}

Text Statistics:
- Words: {stats['total_words']}
- Sentences: {stats['total_sentences']}
- Syllables: {stats['total_syllables']}
- Avg words/sentence: {stats['total_words']/stats['total_sentences']:.1f}
- Avg syllables/word: {stats['total_syllables']/stats['total_words']:.2f}

Overall: {'PASS - Text is readable for target audience' if self.success else 'FAIL - Text may be too complex'}"""
        
        return self.score
    
    def is_successful(self) -> bool:
        """ตรวจสอบว่าผ่านเกณฑ์หรือไม่"""
        return self.success
