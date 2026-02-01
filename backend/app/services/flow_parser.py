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
    def evaluate_pain(data: Dict[str, Any]) -> Dict[str, str]:
        """
        อาการปวด
        Based on: Pain Score and medication effectiveness
        """
        pain_score = data.get('pain_score')
        med_effect = data.get('pain_medication_effect', '')
        print(pain_score, med_effect)
        # Pain Score = 0
        if pain_score == 0:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'Pain Score = 0',
                'recommendation': ''
            }
        
        # Pain Score >= 7
        if pain_score is not None and pain_score >= 7:
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': f'Pain Score = {pain_score} (≥ 7)',
                'recommendation': 'ควรติดต่อทันตแพทย์เพื่อประเมินและปรับแผนการรักษา'
            }
        
        # Pain Score < 7
        # ต้องเช็ก "ไม่ดีขึ้น" ก่อน เพราะ "ไม่ดีขึ้น" มี "ดีขึ้น" อยู่ในคำ
        if 'ไม่ดีขึ้น' in med_effect:
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': f'Pain Score = {pain_score}, ทานยาแล้วไม่ดีขึ้น',
                'recommendation': 'ควรติดต่อทันตแพทย์เพื่อประเมินและปรับแผนการรักษา'
            }
        elif 'ดีขึ้น' in med_effect:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': f'Pain Score = {pain_score}, ทานยาแล้วดีขึ้น',
                'recommendation': 'ทานยาตามแผนเดิม'
            }
        elif 'ไม่ได้ทานยา' in med_effect:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': f'Pain Score = {pain_score}, ยังไม่ได้ทานยา',
                'recommendation': 'แนะนำให้ทานยาแก้ปวดตามที่ทันตแพทย์สั่ง'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ข้อมูลไม่เพียงพอในการประเมิน',
            'recommendation': 'กรุณาระบุข้อมูลให้ครบถ้วน'
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
    def evaluate_swelling(data: Dict[str, Any]) -> Dict[str, str]:
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
                'reason': 'มีอาการหายใจลำบากหรือกลืนลำบาก',
                'recommendation': 'ตัดลวดมัดฟัน และกลับมาพบทันตแพทย์โดยเร็ว'
            }
        
        # บวมมากขึ้นมากจนกระทบการใช้ชีวิตประจำวัน
        if 'บวมมากขึ้นมากๆจนกระทบการใช้ชีวิตประจำวัน' in swelling or 'บวมมากขึ้นมาก' in swelling:
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': 'บวมมากขึ้นมากๆ จนกระทบการใช้ชีวิตประจำวัน',
                'recommendation': 'ควรติดต่อทันตแพทย์โดยเร็ว'
            }
        
        # เช็คว่ามีเลือดออก/รอยช้ำหรือไม่
        has_bleeding = RuleEngine._has_bleeding_or_bruising(data)
        
        # บวมมากขึ้น
        if 'บวมมากขึ้น' in swelling:
            if has_bleeding:
                return {
                    'risk_level': RiskLevel.MEDIUM.value,
                    'reason': 'บวมมากขึ้น และมีอาการเลือดออกหรือรอยช้ำ',
                    'recommendation': 'นอนยกศีรษะสูง 30 องศา'
                }
            else:
                return {
                    'risk_level': RiskLevel.MEDIUM.value,
                    'reason': 'บวมมากขึ้น',
                    'recommendation': 'ประคบอุ่นนอกช่องปาก และนอนยกศีรษะสูง 30 องศา'
                }
        
        # บวมเท่าเดิม
        if 'บวมเท่าเดิม' in swelling:
            if has_bleeding:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'บวมเท่าเดิม และมีอาการเลือดออกหรือรอยช้ำ',
                    'recommendation': 'นอนยกศีรษะสูง 30 องศา'
                }
            else:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'บวมเท่าเดิม',
                    'recommendation': 'ประคบอุ่นนอกช่องปาก และนอนยกศีรษะสูง 30 องศา'
                }
        
        # บวมลดลง/บวมน้อยลง
        if 'บวมลดลง' in swelling or 'บวมน้อยลง' in swelling:
            if has_bleeding:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'บวมลดลง และมีอาการเลือดออกหรือรอยช้ำ',
                    'recommendation': 'นอนยกศีรษะสูง 30 องศา'
                }
            else:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'บวมลดลง',
                    'recommendation': 'ประคบอุ่นนอกช่องปาก และนอนยกศีรษะสูง 30 องศา'
                }
        
        # หายบวมแล้ว
        if 'หายบวมแล้ว' in swelling or 'ปัจจุบันหายบวมแล้ว' in swelling:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'หายบวมแล้ว',
                'recommendation': ''
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ข้อมูลไม่เพียงพอในการประเมิน',
            'recommendation': 'กรุณาระบุข้อมูลให้ครบถ้วน'
        }
    
    @staticmethod
    def evaluate_bleeding(data: Dict[str, Any]) -> Dict[str, str]:
        """
        อาการเลือดซึม/ เลือดออก
        """
        bleeding = data.get('bleeding_status', '')
        
        if 'ไม่มีเลือดซึมหรือไหลแล้ว' in bleeding:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ไม่มีเลือดซึมหรือไหลแล้ว',
                'recommendation': ''
            }
        elif 'เลือดซึม' in bleeding and 'หยุดได้เอง' in bleeding:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'เลือดซึมแต่หยุดได้เอง',
                'recommendation': 'ประคบเย็นนอกช่องปากและนอนยกศีรษะสูง'
            }
        elif 'เลือดสีแดงสดไหลไม่หยุด' in bleeding or 'ปริมาณมาก' in bleeding:
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': 'เลือดสีแดงสดไหลไม่หยุดปริมาณมาก',
                'recommendation': 'กัดผ้าก๊อซให้แน่นหากเลือดออกในช่องปาก หรือก้มหน้าและกดปีกจมูกเข้าหากันหากเลือดออกจากจมูก ร่วมกับประคบเย็นนอกช่องปาก และรีบกลับมาพบทันตแพทย์โดยเร็ว'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ข้อมูลไม่เพียงพอในการประเมิน',
            'recommendation': 'กรุณาระบุข้อมูลให้ครบถ้วน'
        }
    
    @staticmethod
    def evaluate_fever(data: Dict[str, Any]) -> Dict[str, str]:
        """
        อาการไข้
        """
        fever_status = data.get('fever_status', '')
        
        if 'ไม่มีไข้' in fever_status:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ไม่มีไข้',
                'recommendation': ''
            }
        elif 'มีไข้' in fever_status:
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': 'มีไข้ (มากกว่า 38°C)',
                'recommendation': 'ทานยาลดไข้(พาราเซตามอล)'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ไม่ระบุอาการไข้',
            'recommendation': 'กรุณาระบุข้อมูล'
        }
    
    @staticmethod
    def evaluate_numbness(data: Dict[str, Any]) -> Dict[str, str]:
        """
        ชา (numbness) - ไม่มี flow diagram แต่เป็น field ในฟอร์ม
        #ยังไม่มี flow diagram แต่เป็น field ในฟอร์ม
        """
        numbness = data.get('numbness_status', '')
        
        if 'ไม่ชา' in numbness or 'หายแล้ว' in numbness:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ไม่มีอาการชา',
                'recommendation': ''
            }
        elif 'ชา' in numbness:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'มีอาการชา',
                'recommendation': 'สังเกตอาการ หากชานานเกิน 2 สัปดาห์ ควรพบทันตแพทย์'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ไม่ระบุอาการชา',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_phlebitis(data: Dict[str, Any]) -> Dict[str, str]:
        """
        บริเวณที่เอาเข็มน้ำเกลือออกที่หลังมือหรือข้อมือ (phlebitis)
        """
        phlebitis = data.get('phlebitis', '')
        
        if 'ไม่มีอาการ' in phlebitis or 'ไม่มีปวด' in phlebitis:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ไม่มี phlebitis',
                'recommendation': ''
            }
        elif 'มีอาการ' in phlebitis or 'ปวด' in phlebitis or 'บวม' in phlebitis or 'แดง' in phlebitis:
            return {
                'risk_level': RiskLevel.MEDIUM.value,
                'reason': 'มีอาการปวด/บวม/แดง รอบรอยเข็ม',
                'recommendation': 'ประคบเย็นเพื่อลดปวด / ประคบอุ่นเพื่อลดบวม'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ไม่ระบุข้อมูล phlebitis',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_suture(data: Dict[str, Any]) -> Dict[str, str]:
        """
        ไหมเย็บแผล
        """
        suture = data.get('suture_status', '')
        
        if 'แน่นดี' in suture or 'ไม่ได้สังเกต' in suture:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ไหมแน่นดี',
                'recommendation': ''
            }
        elif 'หลุด' in suture and 'ไม่มีเลือด' in suture:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ไหมหลุดบางส่วน แต่ไม่มีเลือดไหล',
                'recommendation': 'ห้ามเขี่ยหรือใช้ลิ้นดุนบริเวณแผล และแจ้งทันตแพทย์หากมีความกังวล'
            }
        elif 'หลุด' in suture and ('เลือด' in suture or 'แดงสด' in suture):
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': 'ไหมหลุด และมีเลือดสีแดงสดไหล',
                'recommendation': 'กัดผ้าก๊อซให้แน่น + ประคบเย็น + กลับมาพบทันตแพทย์โดยเร็ว'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ไม่ระบุสถานะไหม',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_other_symptoms(data: Dict[str, Any]) -> Dict[str, str]:
        """
        อาการอื่นๆ (เลือกได้หลายคำตอบ)
        ตาม flowchart: แต่ละอาการมีระดับความเสี่ยงและคำแนะนำเฉพาะ
        
        COMPLICATED = เกิดเมื่อผู้ป่วยกรอกอาการเพิ่มเติม (Add Another) ที่ไม่อยู่ในรายการมาตรฐาน
                      ผ่าน other_symptoms_custom field
        ลำดับความสำคัญ: HIGH > MEDIUM > COMPLICATED > LOW
        """
        symptoms = data.get('other_symptoms', [])
        if isinstance(symptoms, str):
            symptoms = [symptoms]
        
        # DEBUG: Print other_symptoms_custom
        print(f"🔍 DEBUG other_symptoms_custom RAW: {data.get('other_symptoms_custom')}")
        print(f"🔍 DEBUG other_symptoms: {symptoms}")
        
        # ตรวจสอบว่ามี custom symptoms หรือไม่ (ต้องเช็คก่อนเสมอ)
        custom_symptoms = data.get('other_symptoms_custom', '')
        # แปลง list เป็น string
        if isinstance(custom_symptoms, list):
            custom_symptoms = ', '.join(str(item) for item in custom_symptoms if item)
        custom_symptoms = str(custom_symptoms).strip()
        print(f"🔍 DEBUG custom_symptoms PROCESSED: '{custom_symptoms}'")
        
        # ถ้ามี custom symptoms = COMPLICATED ทันที (ไม่ว่าจะมี standard symptoms หรือไม่)
        if custom_symptoms:
            symptoms_str = ', '.join(symptoms) if symptoms and len(symptoms) > 0 else ''
            if symptoms_str:
                reason = f'มีอาการ: {symptoms_str} และมีอาการอื่นๆที่ผู้ป่วยระบุเพิ่มเติม: {custom_symptoms}'
            else:
                reason = f'มีอาการอื่นๆที่ผู้ป่วยระบุเพิ่มเติม: {custom_symptoms}'
            
            return {
                'risk_level': RiskLevel.COMPLICATED.value,
                'reason': reason,
                'recommendation': 'ควรปรึกษาพยาบาลหรือทันตแพทย์เพื่อประเมินอาการเพิ่มเติม'
            }
        
        # No symptoms
        if not symptoms or len(symptoms) == 0:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ไม่มีอาการอื่นๆ',
                'recommendation': ''
            }
        
        # ความเสี่ยงสูง: ปวดหน่วงบริเวณหน้าแก้ม + น้ำมูกสีเหลือง/เขียว + เหม็นลงคอ
        if any('ปวดหน่วง' in s for s in symptoms):
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': 'ปวดหน่วงบริเวณหน้าแก้ม ร่วมกับมีน้ำมูกสีเหลือง/เขียว เหม็นลงคอ',
                'recommendation': 'งดการสั่งน้ำมูกใช้กระดาษทิชชู่ซับแทน + พบแพทย์'
            }
        
        # ความเสี่ยงกลาง: คลื่นไส้/อาเจียน
        if any('คลื่นไส้' in s or 'อาเจียน' in s for s in symptoms):
            return {
                'risk_level': RiskLevel.MEDIUM.value,
                'reason': 'คลื่นไส้/อาเจียน',
                'recommendation': 'เมื่อมีอาการให้ตะแคงหน้าไปด้านใดด้านหนึ่งเพื่อป้องกันการสำลัก ร่วมกับปรึกษาพยาบาลเพื่อหาสาเหตุและแก้ไข'
            }
        
        # ความเสี่ยงกลาง: มีเสมหะ
        if any('เสมหะ' in s for s in symptoms):
            return {
                'risk_level': RiskLevel.MEDIUM.value,
                'reason': 'มีเสมหะ',
                'recommendation': 'สูดหายใจเข้าเต็มที่และไอให้เสมหะออกมา จิบน้ำอุ่นบ่อยๆ และหากมีอาการทางเดินหายใจมากขึ้นแนะนำตรวจ ATK'
            }
        
        # ความเสี่ยงกลาง: คัดแน่นจมูก
        if any('คัดแน่น' in s or 'จมูก' in s for s in symptoms):
            return {
                'risk_level': RiskLevel.MEDIUM.value,
                'reason': 'คัดแน่นจมูก',
                'recommendation': 'นอนยกศีรษะสูง 30° เลี่ยงอากาศเย็น'
            }
        
        # ความเสี่ยงต่ำ: ช้ำ
        if any('ช้ำ' in s for s in symptoms):
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ช้ำ',
                'recommendation': 'ประคบเย็นกรณีแผลฟกช้ำสีแดงอมม่วง หรือประคบอุ่นหากแผลฟกช้ำเริ่มเป็นสีเขียว โดยประคบนอกช่องปากบริเวณที่ช้ำ'
            }
        
        # ความเสี่ยงต่ำ: ท้องเสีย
        if any('ท้องเสีย' in s or 'ท้องร่วง' in s for s in symptoms):
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ท้องเสีย',
                'recommendation': 'ดื่มน้ำเกลือแร่เพื่อป้องกันภาวะขาดน้ำและเกลือแร่ อุ่นอาหาร ล้างมือเวลาเตรียมอาหาร'
            }
        
        # ความเสี่ยงต่ำ: มีน้ำมูก
        if any('น้ำมูก' in s for s in symptoms):
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'มีน้ำมูก',
                'recommendation': 'งดการสั่งน้ำมูก และใช้กระดาษทิชชู่ซับแทน'
            }
        
        # ความเสี่ยงต่ำ: เจ็บคอ
        if any('เจ็บคอ' in s for s in symptoms):
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'เจ็บคอ',
                'recommendation': 'จิบน้ำบ่อยๆ และหากมีอาการทางเดินหายใจมากขึ้นแนะนำตรวจ ATK'
            }
        
        # ความเสี่ยงต่ำ: น้ำหนักลด
        if any('น้ำหนักลด' in s or 'ผอม' in s for s in symptoms):
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'น้ำหนักลด',
                'recommendation': 'ทานอาหารเสริม เช่น นมเอนชัวร์/โปรตีนชง/ไก่ปั่น/ซุปฟักทอง ร่วมกับแบ่งทานอาหารหลายมื้อ'
            }
        
        # ความเสี่ยงต่ำ: ปวดหัว
        if any('ปวดหัว' in s for s in symptoms):
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ปวดหัว',
                'recommendation': 'ทานยาแก้ปวดตามทันตแพทย์สั่ง'
            }
        
        # อาการทั่วไปอื่นๆ (ไม่อยู่ใน list) -> เป็น LOW
        # (custom_symptoms ถูกเช็คไปแล้วข้างบน)
        symptoms_str = ', '.join(symptoms)
        return {
            'risk_level': RiskLevel.LOW.value,
            'reason': f'มีอาการ: {symptoms_str}',
            'recommendation': 'สังเกตอาการ หากมีอาการรุนแรงขึ้นให้ติดต่อพยาบาล'
        }
    
    @staticmethod
    def evaluate_antibiotic(data: Dict[str, Any]) -> Dict[str, str]:
        """
        รับประทานยาฆ่าเชื้อครบตามแผนการรักษาหรือไม่?
        """
        antibiotic = data.get('antibiotic_compliance', '')
        
        if 'ครบตามแพทย์สั่ง' in antibiotic:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ทานยาฆ่าเชื้อครบ',
                'recommendation': ''
            }
        elif 'ลืม' in antibiotic or 'บางครั้ง' in antibiotic:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ลืมทานยาฆ่าเชื้อบางครั้ง',
                'recommendation': 'รีบทานทันทีที่นึกได้ หากใกล้เวลามื้อถัดไปให้ข้ามมื้อที่ลืม'
            }
        elif 'ไม่ได้ทาน' in antibiotic:
            return {
                'risk_level': RiskLevel.MEDIUM.value,
                'reason': 'ไม่ได้ทานยาฆ่าเชื้อเลย',
                'recommendation': 'แจ้งให้ทันตแพทย์ทราบเพื่อประเมินและปรับแผนการรักษา'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ไม่ระบุการทานยาฆ่าเชื้อ',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_compress(data: Dict[str, Any]) -> Dict[str, str]:
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
                    'reason': 'ประคบเย็นอยู่ และมีอาการเลือดซึม/เลือดออก/รอยช้ำ',
                    'recommendation': 'ประคบเย็นต่อ'
                }
            else:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'ประคบเย็นอยู่ และไม่มีอาการเลือดซึม/เลือดออก/รอยช้ำ',
                    'recommendation': 'เปลี่ยนเป็นประคบอุ่น'
                }
        elif 'ประคบอุ่น' in compress:
            if has_bleeding:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'ประคบอุ่นอยู่ และมีอาการเลือดซึม/เลือดออก/รอยช้ำ',
                    'recommendation': 'เปลี่ยนเป็นประคบเย็น'
                }
            else:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'ประคบอุ่นอยู่ และไม่มีอาการเลือดซึม/เลือดออก/รอยช้ำ',
                    'recommendation': 'ประคบอุ่นต่อ'
                }
        elif 'ไม่ได้ประคบ' in compress:
            if has_bleeding:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'ไม่ได้ประคบ และมีอาการเลือดซึม/เลือดออก/รอยช้ำ',
                    'recommendation': 'เริ่มประคบเย็น'
                }
            else:
                return {
                    'risk_level': RiskLevel.LOW.value,
                    'reason': 'ไม่ได้ประคบ และไม่มีอาการเลือดซึม/เลือดออก/รอยช้ำ',
                    'recommendation': 'เริ่มประคบอุ่น'
                }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ไม่ระบุการประคบ',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_imf(data: Dict[str, Any]) -> Dict[str, str]:
        """
        IMF: มีการมัดฟันบนและล่างเข้าด้วยกันหรือไม่
        """
        has_imf = data.get('has_imf', '')
        wire_status = data.get('imf_wire_status', '')
        
        # ถ้าไม่มี IMF (เช็คหลายรูปแบบ)
        if not has_imf or has_imf == False or 'ไม่มี' in str(has_imf) or has_imf == 'ไม่':
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ไม่มีการมัดฟัน',
                'recommendation': ''
            }
        
        # ถ้ามี IMF แต่ไม่มีข้อมูล wire_status
        if not wire_status or wire_status.strip() == '':
            return {
                'risk_level': RiskLevel.UNKNOWN.value,
                'reason': 'ไม่สามารถประเมิน IMF ได้ (ไม่มีข้อมูลสถานะลวด/ยาง)',
                'recommendation': ''
            }
        
        # ถ้ามี IMF ให้เช็คสถานะลวด
        if 'แน่นดี' in wire_status or 'แน่น' in wire_status or 'ดี' in wire_status:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ลวด/ยางมัดฟันแน่นดี',
                'recommendation': ''
            }
        elif 'หลวม' in wire_status or 'อ้าปากได้' in wire_status:
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': 'ลวดมัดฟันหลวม อ้าปากได้เล็กน้อย',
                'recommendation': ''
            }
        elif 'ยางขาด' in wire_status and 'อ้าปากไม่ได้' in wire_status:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ยางมัดฟันขาดบางเส้น แต่ยังอ้าปากไม่ได้',
                'recommendation': 'สังเกตอาการ หากอ้าปากได้ให้แจ้งทันตแพทย์'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ไม่สามารถประเมิน IMF ได้',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_walking(data: Dict[str, Any]) -> Dict[str, str]:
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
                'reason': 'ไม่ได้ทำหัตถการนำกระดูกสะโพกมาปลูก',
                'recommendation': ''
            }
        
        walking = data.get('walking_status', '')
        
        if 'คล่อง' in walking or 'ปกติ' in walking or 'เดินได้' in walking:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'เดินได้ปกติ',
                'recommendation': ''
            }
        elif 'ไม่ถนัด' in walking:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'เดินไม่ถนัด',
                'recommendation': 'ใช้เวลา ค่อยๆ หายเอง'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ไม่ระบุการเดิน',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_brushing(data: Dict[str, Any]) -> Dict[str, str]:
        """
        การแปรงฟัน
        ตัวเลือก: "แปรงฟันได้" หรือ "แปรงฟันไม่ถนัด"
        """
        brushing = data.get('brushing_teeth', '')
        
        if not brushing or brushing.strip() == '':
            return {
                'risk_level': RiskLevel.UNKNOWN.value,
                'reason': 'ไม่ระบุการแปรงฟัน',
                'recommendation': ''
            }
        
        # แปรงได้แต่ไม่ถนัด
        if 'ไม่ถนัด' in brushing or 'แปรงไม่ถนัด' in brushing or 'แปรงฟันไม่ถนัด' in brushing:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'แปรงฟันไม่ถนัด',
                'recommendation': 'ใช้แปรงหัวเล็กขนนุ่ม + ยาสีฟันไม่แสบ แปรงเบาๆ หลีกเลี่ยงเหงือกที่มีแผล'
            }
        # แปรงได้
        elif 'แปรงได้' in brushing or 'แปรงฟันได้' in brushing or 'ได้' in brushing:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'แปรงฟันได้',
                'recommendation': ''
            }
        
        # Fallback - ถ้ามีคำว่า "แปรง" ก็ถือว่าแปรงได้
        if 'แปรง' in brushing:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'แปรงฟันได้',
                'recommendation': ''
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ไม่ระบุการแปรงฟัน',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_rinsing(data: Dict[str, Any]) -> Dict[str, str]:
        """
        การบ้วนปาก
        """
        rinsing = data.get('mouth_rinsing', '')
        
        if not rinsing or rinsing.strip() == '':
            return {
                'risk_level': RiskLevel.UNKNOWN.value,
                'reason': 'ไม่ระบุการบ้วนปาก',
                'recommendation': ''
            }
        
        # 1. บ้วนปากได้ -> ความเสี่ยงต่ำ (ไม่มีคำแนะนำ)
        if 'บ้วนปากได้' in rinsing or 'บ้วนได้' in rinsing:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'บ้วนปากได้',
                'recommendation': ''
            }
            
        # 2. บ้วนปากไม่ได้ -> ความเสี่ยงต่ำ (ไม่มีคำแนะนำ ตาม Flowchart D2)
        if 'บ้วนปากไม่ได้' in rinsing or 'บ้วนไม่ได้' in rinsing:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'บ้วนปากไม่ได้',
                'recommendation': ''
            }
            
        # 3. ไม่ได้บ้วนปาก -> ความเสี่ยงต่ำ (มีคำแนะนำ ตาม Flowchart D3)
        # Note: Frontend อาจจะยังไม่มีตัวเลือกนี้ แต่ใส่ Logic รองรับไว้
        if 'ไม่ได้บ้วนปาก' in rinsing or 'ไม่ได้บ้วน' in rinsing:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'ไม่ได้บ้วนปาก',
                'recommendation': 'บ้วนปากเบาๆด้วยน้ำเปล่าจามด้วยน้ำยาบ้วนปาก ทุกครั้งหลังทานอาหาร'
            }
        
        # Fallback
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ไม่ระบุการบ้วนปาก',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_feeding(data: Dict[str, Any]) -> Dict[str, str]:
        """
        วิธีการรับประทานอาหาร
        """
        feeding = data.get('feeding_method', '')
        
        if not feeding or feeding.strip() == '':
            return {
                'risk_level': RiskLevel.UNKNOWN.value,
                'reason': 'ไม่ระบุวิธีการรับประทานอาหาร',
                'recommendation': ''
            }
        
        if 'syringe' in feeding.lower() or 'กระบอกฉีด' in feeding or 'ฉีด' in feeding:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'รับประทานอาหารผ่าน syringe',
                'recommendation': ''
            }
        elif 'nasogastric' in feeding.lower() or 'สายยาง' in feeding or 'ng' in feeding.lower() or 'NG' in feeding:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'รับประทานอาหารผ่าน NG tube',
                'recommendation': ''
            }
        elif 'ปกติ' in feeding or 'ได้' in feeding or 'ทาน' in feeding:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'รับประทานอาหารได้ปกติ',
                'recommendation': ''
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ไม่ระบุวิธีการรับประทานอาหาร',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_food_types(data: Dict[str, Any]) -> Dict[str, str]:
        """
        ประเภทอาหารที่ทาน
        """
        food_types = data.get('food_types', [])
        if isinstance(food_types, str):
            food_types = [food_types]
        
        if not food_types or len(food_types) == 0:
            return {
                'risk_level': RiskLevel.UNKNOWN.value,
                'reason': 'ไม่ระบุประเภทอาหาร',
                'recommendation': ''
            }
        
        # All food types are acceptable based on recovery stage
        food_description = ', '.join(food_types)
        return {
            'risk_level': RiskLevel.LOW.value,
            'reason': f'ทานอาหาร: {food_description}',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_food_amount(data: Dict[str, Any]) -> Dict[str, str]:
        """
        ปริมาณอาหารที่ทาน
        """
        amount = data.get('food_amount', '')
        
        if 'ปกติ' in amount:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'รับประทานอาหารปริมาณปกติ',
                'recommendation': ''
            }
        elif 'น้อยลง' in amount or 'ลดลง' in amount:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'รับประทานอาหารได้น้อยลง',
                'recommendation': 'ทานอาหารเสริม เช่น นมเอนชัวร์ และแบ่งทานอาหารหลายมื้อ'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ไม่ระบุปริมาณอาหาร',
            'recommendation': ''
        }
    
    @staticmethod
    def evaluate_ng_tube(data: Dict[str, Any]) -> Dict[str, str]:
        """
        ตำแหน่งสายยางให้อาหาร (NG tube position)
        """
        ng_position = data.get('ng_tube_position', '')
        
        if 'ตำแหน่งเดิม' in ng_position and 'แน่นดี' in ng_position:
            return {
                'risk_level': RiskLevel.LOW.value,
                'reason': 'สายยางอยู่ในตำแหน่งเดิม เทปยึดแน่นดี',
                'recommendation': ''
            }
        elif 'เลื่อน' in ng_position or 'หลุด' in ng_position or 'ไม่แน่น' in ng_position:
            return {
                'risk_level': RiskLevel.HIGH.value,
                'reason': 'สายยางเลื่อนตำแหน่ง หรือเทปไม่แน่น',
                'recommendation': 'ติดต่อพยาบาลหรือแพทย์ทันที'
            }
        
        return {
            'risk_level': RiskLevel.UNKNOWN.value,
            'reason': 'ไม่ระบุตำแหน่งสายยาง',
            'recommendation': ''
        }
    
    def evaluate_flow(self, flow_name: str, data: Dict[str, Any]) -> Dict[str, str]:
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
            'การรับประทานยาเชื้อ': self.evaluate_antibiotic,  # alias duplicate but keep for clarity
            'วิธีการรับประทานอาหาร': self.evaluate_feeding,
            'การรับประทานอาหาร': self.evaluate_feeding,  # alias
            'ประเภทอาหารที่ทาน (สามารถเลือกได้หลายคำตอบ)': self.evaluate_food_types,
            'ปริมาณอาหารที่ทาน': self.evaluate_food_amount,
        }
        
        evaluator = evaluators.get(flow_name)
        if not evaluator:
            return {
                'risk_level': RiskLevel.UNKNOWN.value,
                'reason': f'ไม่พบ flow: {flow_name}',
                'recommendation': ''
            }
        
        return evaluator(data)
    
    def evaluate_all_flows(self, data: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Evaluate all available flows"""
        results = {}
        
        # List of all flows to evaluate
        flow_names = [
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
            'วิธีการรับประทานอาหาร',
            'ประเภทอาหารที่ทาน (สามารถเลือกได้หลายคำตอบ)',
            'ปริมาณอาหารที่ทาน',
        ]
        
        for flow_name in flow_names:
            results[flow_name] = self.evaluate_flow(flow_name, data)
        
        return results

