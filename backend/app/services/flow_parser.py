"""
Rule-Based Risk Classifier
Direct implementation from clinical guidelines (no Mermaid parsing)
Each flow is implemented as a Python function for deterministic evaluation
"""
from typing import Dict, Any
from enum import Enum


class RiskLevel(Enum):
    """
    ลำดับความสำคัญของความเสี่ยง (จากมากไปน้อย):
    1. HIGH (ความเสี่ยงสูง)
    2. MEDIUM (ความเสี่ยงปานกลาง)
    3. COMPLICATED (ซับซ้อน - เกิดเมื่อผู้ป่วยระบุอาการเพิ่มเติมที่ไม่อยู่ในรายการมาตรฐาน)
    4. LOW (ความเสี่ยงต่ำ)
    """
    LOW = "ความเสี่ยงต่ำ"
    MEDIUM = "ความเสี่ยงปานกลาง"
    HIGH = "ความเสี่ยงสูง"
    COMPLICATED = "ไม่สามารถสรุปผลความเสี่ยงได้เนื่องจากอาการมีความซับซ้อน"
    UNKNOWN = "ไม่สามารถประเมินได้"
    NOT_APPLICABLE = "ไม่ต้องประเมิน"


class RuleEngine:
    """Rule-based risk classification engine - direct implementation"""
    
    @staticmethod
    def evaluate_pain(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        อาการปวด
        Based on: Pain Score and medication effectiveness
        """
        pain_score = data.get('pain_score')
        med_effect = data.get('pain_medication_effect', '')
        # Pain Score = 0
        if pain_score == 0:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Pain Score = 0' if language == 'en' else 'Pain Score = 0',
                'recommendation': ''
            }
        
        # Pain Score >= 7
        if pain_score is not None and pain_score >= 7:
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': f'Pain Score = {pain_score} (≥ 7)' if language == 'en' else f'Pain Score = {pain_score} (≥ 7)',
                'recommendation': ''
            }
        
        # Pain Score < 7
        # ต้องเช็ก "ไม่ดีขึ้น" ก่อน เพราะ "ไม่ดีขึ้น" มี "ดีขึ้น" อยู่ในคำ
        if 'ไม่ดีขึ้น' in med_effect:
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': f'Pain Score = {pain_score}, Medication ineffective' if language == 'en' else f'Pain Score = {pain_score}, ทานยาแล้วไม่ดีขึ้น',
                'recommendation': ''
            }
        elif 'ดีขึ้น' in med_effect:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': f'Pain Score = {pain_score}, Improved after medication' if language == 'en' else f'Pain Score = {pain_score}, ทานยาแล้วดีขึ้น',
                'recommendation': 'continue current medication' if language == 'en' else 'ทานยาตามแผนเดิม'
            }
        elif 'ไม่ได้ทานยา' in med_effect:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': f'Pain Score = {pain_score}, No medication taken' if language == 'en' else f'Pain Score = {pain_score}, ยังไม่ได้ทานยา',
                'recommendation': 'take pain medicine as prescribed by your dentist' if language == 'en' else 'แนะนำให้ทานยาแก้ปวดตามที่ทันตแพทย์สั่ง'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'Insufficient data' if language == 'en' else 'ข้อมูลไม่เพียงพอในการประเมิน',
            'recommendation': ''
        }
    
    @staticmethod
    def _has_bleeding_or_bruising(data: Dict[str, Any]) -> bool:
        """
        ตรวจสอบว่ามีอาการเลือดออกหรือรอยช้ำหรือไม่
        """
        # เช็คจากสถานะเลือดออก
        bleeding = data.get('bleeding_status', '')
        if bleeding and 'ไม่มีเลือดซึมหรือไหลแล้ว' not in bleeding:
            # มีเลือดซึมหรือเลือดออกอยู่
            return True
        
        # เช็คจากอาการอื่นๆว่ามี 'ช้ำ' หรือไม่
        symptoms = data.get('other_symptoms', [])
        if isinstance(symptoms, str):
            symptoms = [symptoms]
        if any('ช้ำ' in str(s) for s in symptoms):
            return True
        
        return False
    
    @staticmethod
    def evaluate_swelling(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        อาการบวม
        Based on: breathing difficulty, swelling status, and bleeding/bruising
        """
        breathing = data.get('breathing_or_swallowing_difficulty', '')
        swelling = data.get('swelling_status', '')
        
        # มีอาการหายใจลำบาก หรือ กลืนลำบาก
        if 'มี' in breathing and 'ไม่มี' not in breathing:
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': 'Breathing or swallowing difficulty detected' if language == 'en' else 'มีอาการหายใจลำบากหรือกลืนลำบาก',
                'recommendation': 'cut intermaxillary fixation wires and return to the dentist immediately' if language == 'en' else 'ตัดลวดมัดฟัน และกลับมาพบทันตแพทย์โดยเร็ว'
            }
        
        # บวมมากขึ้นมากจนกระทบการใช้ชีวิตประจำวัน
        if 'บวมมากขึ้นมากๆจนกระทบการใช้ชีวิตประจำวัน' in swelling or 'บวมมากขึ้นมาก' in swelling:
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': 'Severe swelling affecting daily life' if language == 'en' else 'บวมมากขึ้นมากๆ จนกระทบการใช้ชีวิตประจำวัน',
                'recommendation': ''
            }
        
        # เช็คว่ามีเลือดออก/รอยช้ำหรือไม่
        has_bleeding = RuleEngine._has_bleeding_or_bruising(data)
        
        # บวมมากขึ้น
        if 'บวมมากขึ้น' in swelling:
            if has_bleeding:
                return {
                    'risk_level': RiskLevel.MEDIUM.value,
                    'reason': 'Increased swelling with bleeding/bruising' if language == 'en' else 'บวมมากขึ้น และมีอาการเลือดออกหรือรอยช้ำ',
                    'recommendation': 'Sleep with head elevated at 30°' if language == 'en' else 'นอนยกศีรษะสูง 30 องศา'
                }
            else:
                return {
                    'risk_level': RiskLevel.MEDIUM.value,
                    'reason': 'Increased swelling' if language == 'en' else 'บวมมากขึ้น',
                    'recommendation': 'Apply a warm compression outside the mouth and sleep with head elevated at 30' if language == 'en' else 'ประคบอุ่นนอกช่องปาก และนอนยกศีรษะสูง 30 องศา'
                }
        
        # บวมเท่าเดิม
        if 'บวมเท่าเดิม' in swelling:
            if has_bleeding:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'Swelling unchanged with bleeding/bruising' if language == 'en' else 'บวมเท่าเดิม และมีอาการเลือดออกหรือรอยช้ำ',
                    'recommendation': 'Sleep with head elevated at 30°' if language == 'en' else 'นอนยกศีรษะสูง 30 องศา'
                }
            else:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'Swelling unchanged' if language == 'en' else 'บวมเท่าเดิม',
                    'recommendation': 'Apply a warm compression outside the mouth and sleep with head elevated at 30' if language == 'en' else 'ประคบอุ่นนอกช่องปาก และนอนยกศีรษะสูง 30 องศา'
                }
        
        # บวมลดลง/บวมน้อยลง
        if 'บวมลดลง' in swelling or 'บวมน้อยลง' in swelling:
            if has_bleeding:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'Decreased swelling with bleeding/bruising' if language == 'en' else 'บวมลดลง และมีอาการเลือดออกหรือรอยช้ำ',
                    'recommendation': 'Sleep with head elevated at 30°' if language == 'en' else 'นอนยกศีรษะสูง 30 องศา'
                }
            else:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'Decreased swelling' if language == 'en' else 'บวมลดลง',
                    'recommendation': 'Apply a warm compression outside the mouth and sleep with head elevated at 30' if language == 'en' else 'ประคบอุ่นนอกช่องปาก และนอนยกศีรษะสูง 30 องศา'
                }
        
        # หายบวมแล้ว
        if 'หายบวมแล้ว' in swelling or 'ปัจจุบันหายบวมแล้ว' in swelling:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Swelling resolved' if language == 'en' else 'หายบวมแล้ว',
                'recommendation': ''
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'Insufficient data' if language == 'en' else 'ข้อมูลไม่เพียงพอในการประเมิน',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_bleeding(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        อาการเลือดซึม/ เลือดออก
        """
        bleeding = data.get('bleeding_status', '')
        
        if 'ไม่มีเลือดซึมหรือไหลแล้ว' in bleeding:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'No bleeding' if language == 'en' else 'ไม่มีเลือดซึมหรือไหลแล้ว',
                'recommendation': ''
            }
        elif 'เลือดซึม' in bleeding and 'หยุดได้เอง' in bleeding:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Minor bleeding, stopped on its own' if language == 'en' else 'เลือดซึมแต่หยุดได้เอง',
                'recommendation': 'apply a cold compression externally and sleep with head elevated at 30°' if language == 'en' else 'ประคบเย็นนอกช่องปากและนอนยกศีรษะสูง'
            }
        elif 'เลือดสีแดงสดไหลไม่หยุด' in bleeding or 'ปริมาณมาก' in bleeding:
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': 'Uncontrollable excessive bleeding' if language == 'en' else 'เลือดสีแดงสดไหลไม่หยุดปริมาณมาก',
                'recommendation': 'For oral bleeding, bite firmly on gauze; for nasal bleeding, pinch nostrils together while leaning forward. In both cases, apply an external cold compression and return to the dentist immediately' if language == 'en' else 'กัดผ้าก๊อซให้แน่นหากเลือดออกในช่องปาก หรือก้มหน้าและกดปีกจมูกเข้าหากันหากเลือดออกจากจมูก ร่วมกับประคบเย็นนอกช่องปาก และรีบกลับมาพบทันตแพทย์โดยเร็ว'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'Insufficient data' if language == 'en' else 'ข้อมูลไม่เพียงพอในการประเมิน',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_fever(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        อาการไข้
        """
        fever_status = data.get('fever_status', '')
        
        if 'ไม่มีไข้' in fever_status:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'No fever' if language == 'en' else 'ไม่มีไข้',
                'recommendation': ''
            }
        elif 'มีไข้' in fever_status:
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': 'High fever (> 38°C)' if language == 'en' else 'มีไข้ (มากกว่า 38°C)',
                'recommendation': 'take fever-reducing medicine such as paracetamol' if language == 'en' else 'ทานยาลดไข้(พาราเซตามอล)'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'Unspecified fever status' if language == 'en' else 'ไม่ระบุอาการไข้',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_numbness(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        ชา (numbness) - ไม่มี flow diagram แต่เป็น field ในฟอร์ม
        #ยังไม่มี flow diagram แต่เป็น field ในฟอร์ม
        """
        numbness = data.get('numbness_status', '')
        
        if 'ไม่ชา' in numbness or 'หายแล้ว' in numbness:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'No numbness' if language == 'en' else 'ไม่มีอาการชา',
                'recommendation': ''
            }
        elif 'ชา' in numbness:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Numbness persists' if language == 'en' else 'มีอาการชา',
                'recommendation': 'Observe symptoms. If persists more than 2 weeks, see dentist.' if language == 'en' else 'สังเกตอาการ หากชานานเกิน 2 สัปดาห์ ควรพบทันตแพทย์'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'Unspecified numbness' if language == 'en' else 'ไม่ระบุอาการชา',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_phlebitis(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        บริเวณที่เอาเข็มน้ำเกลือออกที่หลังมือหรือข้อมือ (phlebitis)
        """
        phlebitis = data.get('phlebitis', '')
        
        if 'ไม่มีอาการ' in phlebitis or 'ไม่มีปวด' in phlebitis:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'No phlebitis' if language == 'en' else 'ไม่มี phlebitis',
                'recommendation': ''
            }
        elif 'มีอาการ' in phlebitis or 'ปวด' in phlebitis or 'บวม' in phlebitis or 'แดง' in phlebitis:
            return {
                'risk_level': RiskLevel.MEDIUM.value,
                'reason': 'Pain/Swelling/Redness at IV site' if language == 'en' else 'มีอาการปวด/บวม/แดง รอบรอยเข็ม',
                'recommendation': 'apply cold compression to reduce pain or warm compression to reduce swelling' if language == 'en' else 'ประคบเย็นเพื่อลดปวด / ประคบอุ่นเพื่อลดบวม'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'No phlebitis data' if language == 'en' else 'ไม่ระบุข้อมูล phlebitis',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_suture(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        ไหมเย็บแผล
        """
        suture = data.get('suture_status', '')
        
        if 'แน่นดี' in suture or 'ไม่ได้สังเกต' in suture:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Sutures intact' if language == 'en' else 'ไหมแน่นดี',
                'recommendation': ''
            }
        elif 'หลุด' in suture and 'ไม่มีเลือด' in suture:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Partial suture loss, no bleeding' if language == 'en' else 'ไหมหลุดบางส่วน แต่ไม่มีเลือดไหล',
                'recommendation': 'do not touch the wound or push it with your tongue. Contact your dentist if you are concerned (for example, if the wound opens)' if language == 'en' else 'ห้ามเขี่ยหรือใช้ลิ้นดุนบริเวณแผล และแจ้งทันแพทย์หากมีความกังวล เช่น แผลแยก'
            }
        elif 'หลุด' in suture and ('เลือด' in suture or 'แดงสด' in suture):
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': 'Suture loss with fresh bleeding' if language == 'en' else 'ไหมหลุด และมีเลือดสีแดงสดไหล',
                'recommendation': 'bite firmly on gauze at the bleeding area, apply external cold compression, and return to the dentist immediately' if language == 'en' else 'กัดผ้าก๊อซให้แน่นบริเวณที่เลือดไหล ร่วมกับประคบเย็นนอกช่องปาก และกลับมาพบทันตแพทย์โดยเร็ว'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'Unspecified suture status' if language == 'en' else 'ไม่ระบุสถานะไหม',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_other_symptoms(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        อาการอื่นๆ (เลือกได้หลายคำตอบ)
        ตาม flowchart: แต่ละอาการมีระดับความเสี่ยงและคำแนะนำเฉพาะ
        
        COMPLICATED = เกิดเมื่อผู้ป่วยกรอกอาการเพิ่มเติม (Add Another) ที่ไม่อยู่ในรายการมาตรฐาน
                      ผ่าน other_symptoms_custom field
        
        NOTE: ตอนนี้ function นี้จะถูกเรียกแยกสำหรับแต่ละ symptom (มี symptom เดียวใน list)
              ไม่ใช่หลาย symptoms พร้อมกันแล้ว - ดังนั้นไม่ต้อง aggregate
        """
        symptoms = data.get('other_symptoms', [])
        if isinstance(symptoms, str):
            symptoms = [symptoms]
        
        # ตรวจสอบว่ามี custom symptoms หรือไม่ (ต้องเช็คก่อนเสมอ)
        custom_symptoms = data.get('other_symptoms_custom', '')
        # แปลง list เป็น string
        if isinstance(custom_symptoms, list):
            custom_symptoms = ', '.join(str(item) for item in custom_symptoms if item)
        custom_symptoms = str(custom_symptoms).strip()
        
        # ถ้ามี custom symptoms = COMPLICATED ทันที (ไม่ว่าจะมี standard symptoms หรือไม่)
        if custom_symptoms:
            symptoms_str = ', '.join(symptoms) if symptoms and len(symptoms) > 0 else ''
            if symptoms_str:
                reason = f'Symptoms: {symptoms_str} and additional symptoms: {custom_symptoms}' if language == 'en' else f'มีอาการ: {symptoms_str} และมีอาการอื่นๆที่ผู้ป่วยระบุเพิ่มเติม: {custom_symptoms}'
            else:
                reason = f'Additional symptoms reported: {custom_symptoms}' if language == 'en' else f'มีอาการอื่นๆที่ผู้ป่วยระบุเพิ่มเติม: {custom_symptoms}'
            
            return {
                'risk_level': RiskLevel.COMPLICATED.value,
                'reason': reason,
                'recommendation': 'Consult nurse or dentist for further assessment' if language == 'en' else 'ควรปรึกษาพยาบาลหรือทันตแพทย์เพื่อประเมินอาการเพิ่มเติม'
            }
        
        # No symptoms
        if not symptoms or len(symptoms) == 0:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'No other symptoms' if language == 'en' else 'ไม่มีอาการอื่นๆ',
                'recommendation': ''
            }
        
        # เก็บผลลัพธ์ทุกอาการ
        all_results = []
        
        # แมป symptom KEY กับ risk และ recommendation
        # Frontend ส่ง key มา (เช่น 'headache', 'bruising') แทน label
        symptom_map = {
            'sinus_pain': {
                'risk': RiskLevel.HIGH.value,
                'reason_en': 'Cheek pain with yellow/green mucus and bad smell',
                'reason_th': 'ปวดหน่วงบริเวณหน้าแก้ม ร่วมกับมีน้ำมูกสีเหลือง/เขียว เหม็นลงคอ',
                'recommendation_en': 'Do not blow your nose. Gently wipe with tissue instead',
                'recommendation_th': 'งดการสั่งน้ำมูกใช้กระดาษทิชชู่ซับแทน'
            },
            'nausea_vomiting': {
                'risk': RiskLevel.MEDIUM.value,
                'reason_en': 'Nausea/Vomiting',
                'reason_th': 'คลื่นไส้/อาเจียน',
                'recommendation_en': 'During an episode, turn your head to one side to prevent choking and consult a nurse to identify the cause',
                'recommendation_th': 'เมื่อมีอาการให้ตะแคงหน้าไปด้านใดด้านหนึ่งเพื่อป้องกันการสำลัก ร่วมกับปรึกษาพยาบาลเพื่อหาสาเหตุและแก้ไข'
            },
            'cough': {
                'risk': RiskLevel.MEDIUM.value,
                'reason_en': 'Cough/Phlegm',
                'reason_th': 'ไอ/มีเสมหะ',
                'recommendation_en': 'Take deep breaths and cough to clear phlegm. Sip warm water frequently, and taking an ATK test if respiratory symptoms worsen',
                'recommendation_th': 'สูดหายใจเข้าเต็มที่และไอให้เสมหะออกมา จิบน้ำอุ่นบ่อยๆ และหากมีอาการทางเดินหายใจมากขึ้นแนะนำตรวจ ATK'
            },
            'stuffy_nose': {
                'risk': RiskLevel.MEDIUM.value,
                'reason_en': 'Stuffy nose',
                'reason_th': 'คัดแน่นจมูก',
                'recommendation_en': 'Sleep with your head elevated at 30° and avoid cold air',
                'recommendation_th': 'นอนยกศีรษะสูง 30° เลี่ยงอากาศเย็น'
            },
            'bruising': {
                'risk': RiskLevel.LOW.value,
                'reason_en': 'Bruising',
                'reason_th': 'ช้ำ',
                'recommendation_en': 'Apply cold compression if the bruise is red or purple. Use warm compression when it turns green. Apply compression extraorally',
                'recommendation_th': 'ประคบเย็นกรณีแผลฟกช้ำสีแดงอมม่วง หรือประคบอุ่นหากแผลฟกช้ำเริ่มเป็นสีเขียว โดยประคบนอกช่องปากบริเวณที่ช้ำ'
            },
            'diarrhea': {
                'risk': RiskLevel.LOW.value,
                'reason_en': 'Diarrhea',
                'reason_th': 'ท้องเสีย',
                'recommendation_en': 'Drink oral rehydration solution to prevent dehydration. Eat cooked food and wash hands before preparing food',
                'recommendation_th': 'ดื่มน้ำเกลือแร่เพื่อป้องกันภาวะขาดน้ำและเกลือแร่ อุ่นอาหาร ล้างมือเวลาเตรียมอาหาร'
            },
            'runny_nose': {
                'risk': RiskLevel.LOW.value,
                'reason_en': 'Runny nose',
                'reason_th': 'มีน้ำมูก',
                'recommendation_en': 'Do not blow your nose. Gently wipe with tissue instead',
                'recommendation_th': 'งดการสั่งน้ำมูก และใช้กระดาษทิชชู่ซับแทน'
            },
            'sore_throat': {
                'risk': RiskLevel.LOW.value,
                'reason_en': 'Sore throat',
                'reason_th': 'เจ็บคอ',
                'recommendation_en': 'Sip warm water frequently, and taking an ATK test if respiratory symptoms worsen',
                'recommendation_th': 'จิบน้ำบ่อยๆ และหากมีอาการทางเดินหายใจมากขึ้นแนะนำตรวจ ATK'
            },
            'weight_loss': {
                'risk': RiskLevel.LOW.value,
                'reason_en': 'Weight loss',
                'reason_th': 'น้ำหนักลด',
                'recommendation_en': 'Eat small meals more often and choose high-calorie, high-protein foods like nutrition drinks (for example, Ensure), protein shakes, blended chicken, or pumpkin soup.',
                'recommendation_th': 'ทานอาหารเสริม เช่น นมเอนชัวร์/โปรตีนชง/ไก่ปั่น/ซุปฟักทอง ร่วมกับแบ่งทานอาหารหลายมื้อ'
            },
            'headache': {
                'risk': RiskLevel.LOW.value,
                'reason_en': 'Headache',
                'reason_th': 'ปวดหัว',
                'recommendation_en': 'Take pain medicine as prescribed by your dentist.',
                'recommendation_th': 'ทานยาแก้ปวดตามทันตแพทย์สั่ง'
            }
        }
        
        # ตอนนี้แต่ละ symptom จะถูกเรียกแยกกัน (มี symptom เดียวใน list)
        # ดังนั้นไม่ต้อง loop หรือ aggregate แล้ว - ประมวลผล symptom เดียว
        if not symptoms or len(symptoms) == 0:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'No other symptoms' if language == 'en' else 'ไม่มีอาการอื่น',
                'recommendation': ''
            }
        
        # ดึง symptom key ออกมา (เป็น key เช่น "headache", "bruising")
        symptom_key = symptoms[0].strip()
        
        # หา match ใน symptom_map โดยใช้ key โดยตรง
        if symptom_key in symptom_map:
            value = symptom_map[symptom_key]
            return {
                'risk_level': value['risk'],
                'reason': value['reason_en'] if language == 'en' else value['reason_th'],
                'recommendation': value['recommendation_en'] if language == 'en' else value['recommendation_th']
            }
        
        # ถ้าไม่ match = default LOW
        return {
            'risk_level': RiskLevel.LOW.value,
            'reason': f'Symptom: {symptom_key}' if language == 'en' else f'มีอาการ: {symptom_key}',
            'recommendation': 'Observe symptoms. Contact nurse if worsening.' if language == 'en' else 'สังเกตอาการ หากมีอาการรุนแรงขึ้นให้ติดต่อพยาบาล'
        }
    
    @staticmethod
    def evaluate_antibiotic(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        รับประทานยาฆ่าเชื้อครบตามแผนการรักษาหรือไม่?
        """
        antibiotic = data.get('antibiotic_compliance', '')
        
        if 'ครบตามแพทย์สั่ง' in antibiotic:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Antibiotics completed as prescribed' if language == 'en' else 'ทานยาฆ่าเชื้อครบ',
                'recommendation': ''
            }
        elif 'ลืม' in antibiotic or 'บางครั้ง' in antibiotic:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Missed some antibiotic doses' if language == 'en' else 'ลืมทานยาฆ่าเชื้อบางครั้ง',
                'recommendation': 'take the missed dose when remembered. If it is close to the next dose, skip the missed dose and continue as scheduled. Do not take extra medicine.' if language == 'en' else 'รีบทานทันทีที่นึกได้หากใกล้เวลาของมื้อถัดไปให้ข้ามมื้อที่ลืมและทานยาของมื้อถัดไปตามปกติโดยไม่ต้องเพิ่มขนาดยาเพื่อชดเชย'
            }
        elif 'ไม่ได้ทาน' in antibiotic:
            return {
                'risk_level': RiskLevel.MEDIUM.value,
                'reason': 'No antibiotics taken' if language == 'en' else 'ไม่ได้ทานยาฆ่าเชื้อเลย',
                'recommendation': 'inform the dentist so the treatment plan can be reviewed' if language == 'en' else 'แจ้งให้ทันตแพทย์ทราบเพื่อประเมินและปรับแผนการรักษา'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'Unspecified antibiotic compliance' if language == 'en' else 'ไม่ระบุการทานยาฆ่าเชื้อ',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_compress(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        ประคบเย็น หรือ อุ่นอยู่หรือไม่?
        """
        compress = data.get('compress_type', '')
        
        # ตรวจสอบว่ามีอาการเลือดซึม เลือดออกหรือมีรอยช้ำหรือไม่
        has_bleeding = RuleEngine._has_bleeding_or_bruising(data)
        
        if 'ประคบเย็น' in compress:
            if has_bleeding:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'Cold compress with active bleeding/bruising' if language == 'en' else 'ประคบเย็นอยู่ และมีอาการเลือดซึม/เลือดออก/รอยช้ำ',
                    'recommendation': 'Continue cold compression' if language == 'en' else 'ประคบเย็นต่อ'
                }
            else:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'Cold compress without bleeding/bruising' if language == 'en' else 'ประคบเย็นอยู่ และไม่มีอาการเลือดซึม/เลือดออก/รอยช้ำ',
                    'recommendation': ' Switch to warm compression' if language == 'en' else 'เปลี่ยนเป็นประคบอุ่น'
                }
        elif 'ประคบอุ่น' in compress:
            if has_bleeding:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'Warm compress with active bleeding/bruising' if language == 'en' else 'ประคบอุ่นอยู่ และมีอาการเลือดซึม/เลือดออก/รอยช้ำ',
                    'recommendation': 'Switch to cold compression' if language == 'en' else 'เปลี่ยนเป็นประคบเย็น'
                }
            else:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'Warm compress without bleeding/bruising' if language == 'en' else 'ประคบอุ่นอยู่ และไม่มีอาการเลือดซึม/เลือดออก/รอยช้ำ',
                    'recommendation': 'Continue warm compression' if language == 'en' else 'ประคบอุ่นต่อ'
                }
        elif 'ไม่ได้ประคบ' in compress:
            if has_bleeding:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'No compress with active bleeding/bruising' if language == 'en' else 'ไม่ได้ประคบ และมีอาการเลือดซึม/เลือดออก/รอยช้ำ',
                    'recommendation': 'Start cold compression' if language == 'en' else 'เริ่มประคบเย็น'
                }
            else:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'No compress without bleeding/bruising' if language == 'en' else 'ไม่ได้ประคบ และไม่มีอาการเลือดซึม/เลือดออก/รอยช้ำ',
                    'recommendation': 'Start warm compression' if language == 'en' else 'เริ่มประคบอุ่น'
                }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'Unspecified compress status' if language == 'en' else 'ไม่ระบุการประคบ',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_imf(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        IMF: มีการมัดฟันบนและล่างเข้าด้วยกันหรือไม่
        """
        has_imf = data.get('has_imf', '')
        wire_status = data.get('imf_wire_status', '')
        
        # ถ้าไม่มี IMF (เช็คหลายรูปแบบ)
        if not has_imf or has_imf == False or 'ไม่มี' in str(has_imf) or has_imf == 'ไม่':
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'No intermaxillary fixation (IMF)' if language == 'en' else 'ไม่มีการมัดฟัน',
                'recommendation': ''
            }
        
        # ถ้ามี IMF แต่ไม่มีข้อมูล wire_status
        if not wire_status or wire_status.strip() == '':
            return {
                'risk_level': RiskLevel.UNKNOWN.value,
                'reason': 'IMF data incomplete (wire/elastic status missing)' if language == 'en' else 'ไม่สามารถประเมิน IMF ได้ (ไม่มีข้อมูลสถานะลวด/ยาง)',
                'recommendation': ''
            }
        
        # ถ้ามี IMF ให้เช็คสถานะลวด
        if 'แน่นดี' in wire_status or 'แน่น' in wire_status or 'ดี' in wire_status:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'IMF wire/elastic tight' if language == 'en' else 'ลวด/ยางมัดฟันแน่นดี',
                'recommendation': ''
            }
        elif 'หลวม' in wire_status or 'อ้าปากได้' in wire_status:
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': 'IMF wire loose, mouth can open slightly' if language == 'en' else 'ลวดมัดฟันหลวม อ้าปากได้เล็กน้อย',
                'recommendation': ''
            }
        elif 'ยางขาด' in wire_status and 'อ้าปากไม่ได้' in wire_status:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Some elastic bands broken but mouth cannot open' if language == 'en' else 'ยางมัดฟันขาดบางเส้น แต่ยังอ้าปากไม่ได้',
                'recommendation': '' if language == 'en' else ''
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'IMF assessment failed' if language == 'en' else 'ไม่สามารถประเมิน IMF ได้',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_walking(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        การเดิน (สำหรับผู้ป่วยที่ได้รับการรักษาโดยการนำกระดูกสะโพกมาปลูก)
        ถ้าไม่ได้ทำหัตถการนี้ให้ข้าม
        """
        # ตรวจสอบว่าทำหัตถการนี้หรือไม่จาก special_icbg field
        special_icbg = data.get('special_icbg', '')
        
        # ถ้าไม่มีหรือเป็น 'ไม่มี' ก็ไม่ต้องประเมิน
        if not special_icbg or 'ไม่มี' in str(special_icbg) or special_icbg == 'ไม่':
            return {
                'risk_level': RiskLevel.NOT_APPLICABLE.value,
                'reason': 'ICBG not performed' if language == 'en' else 'ไม่ได้ทำหัตถการนำกระดูกสะโพกมาปลูก',
                'recommendation': ''
            }
        
        walking = data.get('walking_status', '')
        
        if 'คล่อง' in walking or 'ปกติ' in walking or 'เดินได้' in walking:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Walking normally' if language == 'en' else 'เดินได้ปกติ',
                'recommendation': ''
            }
        elif 'ไม่ถนัด' in walking:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Difficulty walking' if language == 'en' else 'เดินไม่ถนัด',
                'recommendation': ''
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'Unspecified walking status' if language == 'en' else 'ไม่ระบุการเดิน',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_brushing(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        การแปรงฟัน
        ตัวเลือก: "แปรงฟันได้" หรือ "แปรงฟันไม่ถนัด"
        """
        brushing = data.get('brushing_teeth', '')
        
        if not brushing or brushing.strip() == '':
            return {
                'risk_level': RiskLevel.UNKNOWN.value,
                'reason': 'Unspecified brushing status' if language == 'en' else 'ไม่ระบุการแปรงฟัน',
                'recommendation': ''
            }
        
        # แปรงได้แต่ไม่ถนัด
        if 'ไม่ถนัด' in brushing or 'แปรงไม่ถนัด' in brushing or 'แปรงฟันไม่ถนัด' in brushing:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Difficulty brushing teeth' if language == 'en' else 'แปรงฟันไม่ถนัด',
                'recommendation': 'Use a small, soft toothbrush with non-irritating toothpaste. Brush gently and slowly. Avoid brushing over surgical wound' if language == 'en' else 'ใช้แปรงสีฟันหัวเล็กขนนุ่มร่วมกับยาสีฟันที่ไม่แสบปาก แปรงเบาๆช้าๆและหลีกเลี่ยงการแปรงโดนเหงือกที่มีแผลโดยใช้น้ำเกลือฉีดล้างแทน'
            }
        # แปรงได้
        elif 'แปรงได้' in brushing or 'แปรงฟันได้' in brushing or 'ได้' in brushing:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Can brush teeth normally' if language == 'en' else 'แปรงฟันได้',
                'recommendation': ''
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'Unspecified brushing status' if language == 'en' else 'ไม่ระบุการแปรงฟัน',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_rinsing(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        การบ้วนปาก
        """
        rinsing = data.get('mouth_rinsing', '')
        
        if not rinsing or rinsing.strip() == '':
            return {
                'risk_level': RiskLevel.UNKNOWN.value,
                'reason': 'Unspecified rinsing status' if language == 'en' else 'ไม่ระบุการบ้วนปาก',
                'recommendation': ''
            }
        
        # 1. บ้วนปากได้ -> ความเสี่ยงต่ำ (ไม่มีคำแนะนำ)
        if 'บ้วนปากได้' in rinsing or 'บ้วนได้' in rinsing:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Can rinse mouth' if language == 'en' else 'บ้วนปากได้',
                'recommendation': ''
            }
            
        # 2. บ้วนปากไม่ได้ -> ความเสี่ยงต่ำ (ไม่มีคำแนะนำ ตาม Flowchart D2)
        if 'บ้วนปากไม่ได้' in rinsing or 'บ้วนไม่ได้' in rinsing:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Cannot rinse mouth' if language == 'en' else 'บ้วนปากไม่ได้',
                'recommendation': ''
            }
            
        # 3. ไม่ได้บ้วนปาก -> ความเสี่ยงต่ำ (มีคำแนะนำ ตาม Flowchart D3)
        # Note: Frontend อาจจะยังไม่มีตัวเลือกนี้ แต่ใส่ Logic รองรับไว้
        if 'ไม่ได้บ้วนปาก' in rinsing or 'ไม่ได้บ้วน' in rinsing:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Not rinsing mouth' if language == 'en' else 'ไม่ได้บ้วนปาก',
                'recommendation': 'Gently rinse with water or mouthwash after every meal' if language == 'en' else 'บ้วนปากเบาๆด้วยน้ำเปล่าจามด้วยน้ำยาบ้วนปาก ทุกครั้งหลังทานอาหาร'
            }
        
        # Fallback
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'Unspecified rinsing status' if language == 'en' else 'ไม่ระบุการบ้วนปาก',
            'recommendation': ''
        }
    
    
    @staticmethod
    def evaluate_food_types(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        ประเภทอาหารที่ทาน
        """
        food_types = data.get('food_types', [])
        if isinstance(food_types, str):
            food_types = [food_types]
        
        if not food_types or len(food_types) == 0:
            return {
                'risk_level': RiskLevel.UNKNOWN.value,
                'reason': 'Unspecified food types' if language == 'en' else 'ไม่ระบุประเภทอาหาร',
                'recommendation': ''
            }
        
        # All food types are acceptable based on recovery stage
        food_description = ', '.join(food_types)
        return {
            'risk_level': RiskLevel.LOW.value,
            'reason': f'Food types: {food_description}' if language == 'en' else f'ทานอาหาร: {food_description}',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_food_amount(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        ปริมาณอาหารที่ทาน
        """
        amount = data.get('food_amount', '')
        
        if 'ปกติ' in amount:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Eating normal amount' if language == 'en' else 'รับประทานอาหารปริมาณปกติ',
                'recommendation': ''
            }
        elif 'น้อยลง' in amount or 'ลดลง' in amount:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Eating less' if language == 'en' else 'รับประทานอาหารได้น้อยลง',
                'recommendation': 'Eat small meals more often and choose high-calorie, high-protein foods such as nutrition drinks (e.g., Ensure), protein shakes, blended chicken, or pumpkin soup' if language == 'en' else 'ทานอาหารเสริม เช่น นมเอนชัวร์ และแบ่งทานอาหารหลายมื้อ'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'Unspecified food amount' if language == 'en' else 'ไม่ระบุปริมาณอาหาร',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_ng_tube(data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """
        ตำแหน่งสายยางให้อาหาร (NG tube position)
        """
        ng_position = data.get('ng_tube_position', '')
        
        if 'ตำแหน่งเดิม' in ng_position and 'แน่นดี' in ng_position:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'NG tube in place, tape tight' if language == 'en' else 'สายยางอยู่ในตำแหน่งเดิม เทปยึดแน่นดี',
                'recommendation': ''
            }
        elif 'เลื่อน' in ng_position or 'หลุด' in ng_position or 'ไม่แน่น' in ng_position:
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': 'NG tube displaced or tape loose' if language == 'en' else 'สายยางเลื่อนตำแหน่ง หรือเทปไม่แน่น',
                'recommendation': ''
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'Unspecified NG tube position' if language == 'en' else 'ไม่ระบุตำแหน่งสายยาง',
            'recommendation': ''
        }
    
    def evaluate_flow(self, flow_name: str, data: Dict[str, Any], language: str = 'th') -> Dict[str, str]:
        """Evaluate a single flow with structured data"""
        # Map flow name to evaluation function
        evaluators = {
            'อาการปวด': self.evaluate_pain,
            'อาการบวม': self.evaluate_swelling,
            'อาการเลือดซึม/ เลือดออก': self.evaluate_bleeding,
            'อาการเลือดออก': self.evaluate_bleeding,
            'อาการไข้': self.evaluate_fever,
            'ชา': self.evaluate_numbness,
            'อาการชา': self.evaluate_numbness,
            'บริเวณที่เอาเข็มน้ำเกลือออกที่หลังมือหรือข้อมือ (phlebitis)': self.evaluate_phlebitis,
            'ไหมเย็บแผล': self.evaluate_suture,
            'อาการอื่นๆ (เลือกได้หลายคำตอบ)': self.evaluate_other_symptoms,
            'การอื่นๆ': self.evaluate_other_symptoms,  # alias
            'รับประทานยาฆ่าเชื้อครบตามแผนการรักษาหรือไม่?': self.evaluate_antibiotic,
            'การรับประทานยาเชื้อ': self.evaluate_antibiotic,  # alias
            'การรับประทานยาฆ่าเชื้อ': self.evaluate_antibiotic,  # alias
            'ประคบเย็น หรือ อุ่นอยู่หรือไม่?': self.evaluate_compress,
            'การประคบ': self.evaluate_compress,  # alias
            'หากมีการมัดฟันบนและล่างเข้าด้วยกัน ลวดมัดฟันแน่นดีหรือไม่?': self.evaluate_imf,
            'IMF': self.evaluate_imf,
            'สถานะลวดมัดฟัน (IMF)': self.evaluate_imf,  # alias
            'การเดิน: การรักษาการแหว่งของสันเหงือกโดยการนำกระดูกสะโพกมาปลูก': self.evaluate_walking,
            'การเดิน': self.evaluate_walking,  # alias
            'ตำแหน่งสายยางให้อาหาร: กรณีในผู้ป่วยที่รับประทานอาหารผ่านทางสายยาง (on NG-nasogastric tube)': self.evaluate_ng_tube,
            'คำถามสายยาง (NG tube)': self.evaluate_ng_tube,  # alias
            'การแปรงฟัน': self.evaluate_brushing,
            'การบ้วนปาก': self.evaluate_rinsing,
            'ประเภทอาหารที่ทาน (สามารถเลือกได้หลายคำตอบ)': self.evaluate_food_types,
            'ปริมาณอาหารที่ทาน': self.evaluate_food_amount,
        }
        
        evaluator = evaluators.get(flow_name)
        if not evaluator:
            return {
                'risk_level': RiskLevel.UNKNOWN.value,
                'reason': f'Flow not found: {flow_name}' if language == 'en' else f'ไม่พบ flow: {flow_name}',
                'recommendation': ''
            }
        
        try:
            return evaluator(data, language=language)
        except Exception as e:
            # Handle errors gracefully
            return {
                'risk_level': RiskLevel.UNKNOWN.value,
                'reason': f'Error evaluating flow: {str(e)}' if language == 'en' else f'เกิดข้อผิดพลาดในการประเมิน: {str(e)}',
                'recommendation': ''
            }
    
    @staticmethod
    def get_flow_names() -> list:
        """Get list of all available flow names"""
        return [
            'อาการปวด',
            'อาการบวม',
            'อาการเลือดออก',
            'อาการไข้',
            'ชา',
            'บริเวณที่เอาเข็มน้ำเกลือออกที่หลังมือหรือข้อมือ (phlebitis)',
            'ไหมเย็บแผล',
            'อาการอื่นๆ (เลือกได้หลายคำตอบ)',
            'รับประทานยาฆ่าเชื้อครบตามแผนการรักษาหรือไม่?',
            'ประคบเย็น หรือ อุ่นอยู่หรือไม่?',
            'หากมีการมัดฟันบนและล่างเข้าด้วยกัน ลวดมัดฟันแน่นดีหรือไม่?',
            'การเดิน: การรักษาการแหว่งของสันเหงือกโดยการนำกระดูกสะโพกมาปลูก',
            'ตำแหน่งสายยางให้อาหาร: กรณีในผู้ป่วยที่รับประทานอาหารผ่านทางสายยาง (on NG-nasogastric tube)',
            'การแปรงฟัน',
            'การบ้วนปาก',
            'ประเภทอาหารที่ทาน (สามารถเลือกได้หลายคำตอบ)',
            'ปริมาณอาหารที่ทาน',
        ]
    
    def evaluate_all_flows(self, data: Dict[str, Any], language: str = 'th') -> Dict[str, Dict[str, str]]:
        """Evaluate all available flows"""
        results = {}
        
        # Get all flow names
        flow_names = self.get_flow_names()
        
        for flow_name in flow_names:
            results[flow_name] = self.evaluate_flow(flow_name, data, language=language)
        
        return results

