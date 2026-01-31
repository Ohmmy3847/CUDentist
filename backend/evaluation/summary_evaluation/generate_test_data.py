"""
Generate 100 programmatic test cases for LLM evaluation
"""
import csv
import random
import os
from datetime import datetime, timedelta
from typing import List, Dict

# ข้อมูลพื้นฐาน
GENDERS = ["ชาย", "หญิง"]
PROCEDURES = [
    "Orthognathic surgery (ผ่าตัดขากรรไกร)",
    "Cleft lip repair (ผ่าตัดปากแหว่ง)",
    "Cleft palate repair (ผ่าตัดเพดานโหว่)",
    "Alveolar bone graft (ปลูกกระดูกสันเหงือก)",
    "Iliac crest bone graft (ICBG) (นำกระดูกสะโพกมาปลูก)"
]

# คำตอบสำหรับแต่ละคำถาม
PAIN_SCORES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
PAIN_MEDICATION = ["ดีขึ้น", "ไม่ดีขึ้น", "ยังไม่ได้ทาน"]
SWELLING_STATUS = [
    "บวมมากขึ้นมากๆจนกระทบการใช้ชีวิต",
    "บวมมากขึ้น",
    "บวมเท่าเดิม",
    "บวมน้อยลง",
    "หายบวมแล้ว"
]
BREATHING_ISSUES = ["มีอาการหายใจลำบากหรือกลืนลำบาก", "ไม่มี"]
BLEEDING_STATUS = [
    "ไม่มีเลือดซึมหรือไหลแล้ว",
    "เลือดซึมแต่หยุดได้เอง",
    "เลือดสีแดงสดไหลไม่หยุดปริมาณมาก"
]
FEVER_STATUS = ["ไม่มีไข้", "มีไข้ (มากกว่า 38 องศาเซลเซียส)"]
PHLEBITIS = [
    "ไม่มีอาการปวด/บวม/แดง รอบรอยเข็ม",
    "มีอาการปวด/บวม/แดง รอบรอยเข็ม"
]
SUTURE_STATUS = [
    "ไหมแน่นดี / ไม่ได้สังเกต",
    "ไหมหลุดหายไปบางส่วน แต่ไม่มีเลือดไหล",
    "ไหมหลุดหายไปบางส่วน และมีอาการเลือดสีแดงสดไหล"
]
OTHER_SYMPTOMS = [
    [],
    ["ช้ำ"],
    ["มีน้ำมูก"],
    ["คัดแน่นจมูก"],
    ["คลื่นไส้/อาเจียน"],
    ["ปวดหัว"],
    ["มีเสมหะ"],
    ["ปวดหน่วงบริเวณหน้าแก้ม ร่วมกับมีน้ำมูกสีเหลือง/เขียว เหม็นลงคอ"]
]
ANTIBIOTIC = ["ครบทุกเม็ด", "ลืมทานบางครั้ง", "ไม่ได้ทานเลย"]
COMPRESS = ["ประคบเย็นอยู่", "ประคบอุ่นอยู่", "ไม่ได้ประคบอะไรเลย"]
IMF_STATUS = ["มีการมัดฟัน", "ไม่มีการมัดฟัน"]
IMF_WIRE = [
    "ลวด/ยางมัดฟันแน่นดี",
    "ลวด/ยางมัดฟันหลวม อ้าปากได้เล็กน้อย",
    "ยางมัดฟันขาดไปบางเส้น แต่ยังอ้าปากไม่ได้"
]
ICBG_STATUS = ["มี", "ไม่มี"]
WALKING = ["เดินได้คล่อง", "เดินไม่ถนัด"]
NG_TUBE_STATUS = ["มี", "ไม่มี"]
NG_POSITION = [
    "สายยางอยู่ในตำแหน่งเดิม,  เทปยึดจมูกกับสายแน่นดี ไม่เลื่อนหลุด",
    "สายยางเลื่อนตำแหน่ง, เทปยึดจมูกกับสายไม่แน่น, เลื่อนหลุด"
]
BRUSHING = ["แปรงฟันได้", "แปรงฟันไม่ได้"]
RINSING = ["บ้วนปากได้", "บ้วนปากไม่ได้", "ไม่ได้บ้วนปาก"]
EATING_METHOD = [
    "รับประทานอาหารผ่านกระบอกฉีดยา (syringe)",
    "รับประทานอาหารผ่านสายยาง (nasogastric tube)",
    "รับประทานอาหารได้ปกติ"
]


def generate_high_risk_case(case_id: int) -> Dict:
    """สร้างกรณีความเสี่ยงสูง"""
    age = random.randint(18, 60)
    gender = random.choice(GENDERS)
    surgery_date = (datetime.now() - timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d")
    procedure = random.choice(PROCEDURES)
    
    # High risk factors
    case = {
        "case_id": f"case_{case_id:03d}",
        # Personal Info
        "first_name": f"ผู้ป่วย",
        "last_name": f"{case_id:03d}",
        "email": None,
        "phone": f"08{random.randint(10000000, 99999999)}",
        "birth_year": None,
        # Basic Medical Info
        "age": age,
        "gender": gender,
        "hn": None,
        "procedures": procedure,
        "surgery_date": surgery_date,
        "discharge_date": None,
        "note": None,
        # Special Procedures
        "has_imf": random.choice(IMF_STATUS),
        "imf_type": None,
        "imf_loops": None,
        "special_icbg": random.choice(ICBG_STATUS),
        "special_icbg_description": None,
        "special_ng_tube": random.choice(NG_TUBE_STATUS),
        "special_ng_tube_description": None,
        # Assessment Data
        "pain_score": random.choice([7, 8, 9, 10]),  # High pain
        "pain_score_description": None,
        "pain_medication_effect": random.choice(["ไม่ดีขึ้น", "ไม่ได้ทานยาแก้ปวด"]),
        "swelling_status": random.choice(["บวมมากขึ้นมากๆจนกระทบการใช้ชีวิตประจำวัน", "บวมมากขึ้น"]),
        "swelling_description": None,
        "breathing_or_swallowing_difficulty": random.choice(["มี", "ไม่มี"]),
        "breathing_description": None,
        "bleeding_status": random.choice(["เลือดสีแดงสดไหลไม่หยุดปริมาณมาก", "เลือดซึม แต่หยุดได้เอง"]),
        "bleeding_description": None,
        "fever_status": random.choice(["มีไข้ (มากกว่า 38 องศาเซลเซียส)", "ไม่มีไข้"]),
        "fever_description": None,
        "numbness_status": None,
        "numbness_description": None,
        "phlebitis": random.choice(PHLEBITIS),
        "phlebitis_description": None,
        "suture_status": random.choice(["ไหมหลุดหายไปบางส่วน และมีอาการเลือดสีแดงสดไหล", "ไหมแน่นดี / ไม่ได้สังเกต"]),
        "suture_description": None,
        "other_symptoms": random.choice([[], ["คลื่นไส้/อาเจียน"], ["ปวดหน่วงบริเวณหน้าแก้ม ร่วมกับมีน้ำมูกสีเหลือง/เขียว เหม็นลงคอ"]]),
        "other_symptoms_custom": None,
        "antibiotic_compliance": random.choice(ANTIBIOTIC),
        "antibiotic_description": None,
        "compress_type": random.choice(COMPRESS),
        "imf_wire_status": random.choice(IMF_WIRE) if random.random() > 0.5 else "",
        "imf_wire_description": None,
        "walking_status": random.choice(WALKING) if random.random() > 0.5 else "",
        "walking_description": None,
        "ng_tube_position": random.choice(NG_POSITION) if random.random() > 0.5 else "",
        "ng_tube_description": None,
        "brushing_teeth": random.choice(BRUSHING),
        "brushing_description": None,
        "mouth_rinsing": random.choice(RINSING),
        "rinsing_description": None,
        "feeding_method": random.choice(EATING_METHOD),
        "feeding_description": None,
        "food_types": None,
        "food_types_custom": None,
        "food_amount": None,
        "food_amount_description": None,
        "additional_questions": None,
        "expected_risk_level": "high"
    }
    return case


def generate_medium_risk_case(case_id: int) -> Dict:
    """สร้างกรณีความเสี่ยงปานกลาง"""
    age = random.randint(18, 60)
    gender = random.choice(GENDERS)
    surgery_date = (datetime.now() - timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d")
    procedure = random.choice(PROCEDURES)
    
    case = {
        "case_id": f"case_{case_id:03d}",
        # Personal Info
        "first_name": f"ผู้ป่วย",
        "last_name": f"{case_id:03d}",
        "email": None,
        "phone": f"08{random.randint(10000000, 99999999)}",
        "birth_year": None,
        # Basic Medical Info
        "age": age,
        "gender": gender,
        "hn": None,
        "procedures": procedure,
        "surgery_date": surgery_date,
        "discharge_date": None,
        "note": None,
        # Special Procedures
        "has_imf": random.choice(IMF_STATUS),
        "imf_type": None,
        "imf_loops": None,
        "special_icbg": random.choice(ICBG_STATUS),
        "special_icbg_description": None,
        "special_ng_tube": random.choice(NG_TUBE_STATUS),
        "special_ng_tube_description": None,
        # Assessment Data
        "pain_score": random.choice([4, 5, 6]),  # Medium pain
        "pain_score_description": None,
        "pain_medication_effect": random.choice(["ดีขึ้น", "ไม่ดีขึ้น"]),
        "swelling_status": random.choice(["บวมมากขึ้น", "บวมเท่าเดิม"]),
        "swelling_description": None,
        "breathing_or_swallowing_difficulty": "ไม่มี",
        "breathing_description": None,
        "bleeding_status": random.choice(["เลือดซึม แต่หยุดได้เอง", "ไม่มีเลือดซึมหรือไหลแล้ว"]),
        "bleeding_description": None,
        "fever_status": "ไม่มีไข้",
        "fever_description": None,
        "numbness_status": None,
        "numbness_description": None,
        "phlebitis": random.choice(["มีอาการปวด/บวม/แดง รอบรอยเข็ม", "ไม่มีอาการปวด/บวม/แดง รอบรอยเข็ม"]),
        "phlebitis_description": None,
        "suture_status": random.choice(["ไหมหลุดหายไปบางส่วน แต่ไม่มีเลือดไหล", "ไหมแน่นดี / ไม่ได้สังเกต"]),
        "suture_description": None,
        "other_symptoms": random.choice([[], ["คัดแน่นจมูก"], ["มีเสมหะ"], ["คลื่นไส้/อาเจียน"]]),
        "other_symptoms_custom": None,
        "antibiotic_compliance": random.choice(["ครบตามแพทย์สั่ง", "ลืมทานบางครั้ง"]),
        "antibiotic_description": None,
        "compress_type": random.choice(COMPRESS),
        "imf_wire_status": "ลวด/ยางมัดฟันแน่นดี" if random.random() > 0.5 else "",
        "imf_wire_description": None,
        "walking_status": random.choice(WALKING) if random.random() > 0.5 else "",
        "walking_description": None,
        "ng_tube_position": "สายยางอยู่ในตำแหน่งเดิม,  เทปยึดจมูกกับสายแน่นดี ไม่เลื่อนหลุด" if random.random() > 0.5 else "",
        "ng_tube_description": None,
        "brushing_teeth": random.choice(BRUSHING),
        "brushing_description": None,
        "mouth_rinsing": random.choice(RINSING),
        "rinsing_description": None,
        "feeding_method": random.choice(EATING_METHOD),
        "feeding_description": None,
        "food_types": None,
        "food_types_custom": None,
        "food_amount": None,
        "food_amount_description": None,
        "additional_questions": None,
        "expected_risk_level": "medium"
    }
    return case


def generate_low_risk_case(case_id: int) -> Dict:
    """สร้างกรณีความเสี่ยงต่ำ"""
    age = random.randint(18, 60)
    gender = random.choice(GENDERS)
    surgery_date = (datetime.now() - timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d")
    procedure = random.choice(PROCEDURES)
    
    case = {
        "case_id": f"case_{case_id:03d}",
        # Personal Info
        "first_name": f"ผู้ป่วย",
        "last_name": f"{case_id:03d}",
        "email": None,
        "phone": f"08{random.randint(10000000, 99999999)}",
        "birth_year": None,
        # Basic Medical Info
        "age": age,
        "gender": gender,
        "hn": None,
        "procedures": procedure,
        "surgery_date": surgery_date,
        "discharge_date": None,
        "note": None,
        # Special Procedures
        "has_imf": random.choice(IMF_STATUS),
        "imf_type": None,
        "imf_loops": None,
        "special_icbg": random.choice(ICBG_STATUS),
        "special_icbg_description": None,
        "special_ng_tube": random.choice(NG_TUBE_STATUS),
        "special_ng_tube_description": None,
        # Assessment Data
        "pain_score": random.choice([0, 1, 2, 3]),  # Low pain
        "pain_score_description": None,
        "pain_medication_effect": random.choice(["ดีขึ้น", "ไม่ได้ทานยาแก้ปวด"]),
        "swelling_status": random.choice(["บวมลดลง", "ปัจจุบันหายบวมแล้ว", "บวมเท่าเดิม"]),
        "swelling_description": None,
        "breathing_or_swallowing_difficulty": "ไม่มี",
        "breathing_description": None,
        "bleeding_status": random.choice(["ไม่มีเลือดซึมหรือไหลแล้ว", "เลือดซึม แต่หยุดได้เอง"]),
        "bleeding_description": None,
        "fever_status": "ไม่มีไข้",
        "fever_description": None,
        "numbness_status": None,
        "numbness_description": None,
        "phlebitis": "ไม่มีอาการปวด/บวม/แดง รอบรอยเข็ม",
        "phlebitis_description": None,
        "suture_status": "ไหมแน่นดี / ไม่ได้สังเกต",
        "suture_description": None,
        "other_symptoms": random.choice([[], ["มีน้ำมูก"], ["ปวดหัว"]]),
        "other_symptoms_custom": None,
        "antibiotic_compliance": "ครบตามแพทย์สั่ง",
        "antibiotic_description": None,
        "compress_type": random.choice(COMPRESS),
        "imf_wire_status": "ลวด/ยางมัดฟันแน่นดี" if random.random() > 0.5 else "",
        "imf_wire_description": None,
        "walking_status": "เดินได้ปกติ" if random.random() > 0.5 else "",
        "walking_description": None,
        "ng_tube_position": "สายยางอยู่ในตำแหน่งเดิม,  เทปยึดจมูกกับสายแน่นดี ไม่เลื่อนหลุด" if random.random() > 0.5 else "",
        "ng_tube_description": None,
        "brushing_teeth": "แปรงฟันได้",
        "brushing_description": None,
        "mouth_rinsing": "บ้วนปากได้",
        "rinsing_description": None,
        "feeding_method": random.choice(EATING_METHOD),
        "feeding_description": None,
        "food_types": None,
        "food_types_custom": None,
        "food_amount": None,
        "food_amount_description": None,
        "additional_questions": None,
        "expected_risk_level": "low"
    }
    return case


def generate_complicated_case(case_id: int) -> Dict:
    """สร้างกรณีซับซ้อน - มีหลายอาการร่วมกัน"""
    age = random.randint(18, 60)
    gender = random.choice(GENDERS)
    surgery_date = (datetime.now() - timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d")
    procedure = random.choice(PROCEDURES)
    
    case = {
        "case_id": f"case_{case_id:03d}",
        # Personal Info
        "first_name": f"ผู้ป่วย",
        "last_name": f"{case_id:03d}",
        "email": None,
        "phone": f"08{random.randint(10000000, 99999999)}",
        "birth_year": None,
        # Basic Medical Info
        "age": age,
        "gender": gender,
        "hn": None,
        "procedures": procedure,
        "surgery_date": surgery_date,
        "discharge_date": None,
        "note": None,
        # Special Procedures
        "has_imf": random.choice(IMF_STATUS),
        "imf_type": None,
        "imf_loops": None,
        "special_icbg": random.choice(ICBG_STATUS),
        "special_icbg_description": None,
        "special_ng_tube": random.choice(NG_TUBE_STATUS),
        "special_ng_tube_description": None,
        # Assessment Data - Complicated: มีหลายอาการร่วมกัน
        "pain_score": random.choice([5, 6, 7, 8]),  # Medium-High pain
        "pain_score_description": None,
        "pain_medication_effect": random.choice(["ไม่ดีขึ้น", "ดีขึ้น"]),
        "swelling_status": random.choice(["บวมมากขึ้น", "บวมเท่าเดิม"]),
        "swelling_description": None,
        "breathing_or_swallowing_difficulty": random.choice(["มี", "ไม่มี"]),
        "breathing_description": None,
        "bleeding_status": random.choice(["เลือดซึม แต่หยุดได้เอง", "เลือดสีแดงสดไหลไม่หยุดปริมาณมาก"]),
        "bleeding_description": None,
        "fever_status": random.choice(["มีไข้ (มากกว่า 38 องศาเซลเซียส)", "ไม่มีไข้"]),
        "fever_description": None,
        "numbness_status": None,
        "numbness_description": None,
        "phlebitis": random.choice(PHLEBITIS),
        "phlebitis_description": None,
        "suture_status": random.choice(SUTURE_STATUS),
        "suture_description": None,
        "other_symptoms": random.choice([
            ["คลื่นไส้/อาเจียน", "ปวดหัว"],
            ["ปวดหน่วงบริเวณหน้าแก้ม ร่วมกับมีน้ำมูกสีเหลือง/เขียว เหม็นลงคอ"],
            ["คัดแน่นจมูก", "มีเสมหะ"],
        ]),  # มักมีหลายอาการ
        "other_symptoms_custom": None,
        "antibiotic_compliance": random.choice(ANTIBIOTIC),
        "antibiotic_description": None,
        "compress_type": random.choice(COMPRESS),
        "imf_wire_status": random.choice(IMF_WIRE) if random.random() > 0.3 else "",
        "imf_wire_description": None,
        "walking_status": random.choice(WALKING) if random.random() > 0.3 else "",
        "walking_description": None,
        "ng_tube_position": random.choice(NG_POSITION) if random.random() > 0.3 else "",
        "ng_tube_description": None,
        "brushing_teeth": random.choice(BRUSHING),
        "brushing_description": None,
        "mouth_rinsing": random.choice(RINSING),
        "rinsing_description": None,
        "feeding_method": random.choice(EATING_METHOD),
        "feeding_description": None,
        "food_types": None,
        "food_types_custom": None,
        "food_amount": None,
        "food_amount_description": None,
        "additional_questions": None,
        "expected_risk_level": "complicated"
    }
    return case


def generate_test_cases(n_cases: int = 100) -> List[Dict]:
    """
    สร้าง test cases โดยแบ่งสัดส่วน:
    - 30% High Risk
    - 25% Medium Risk
    - 25% Complicated
    - 20% Low Risk
    """
    cases = []
    
    # Stratified sampling
    n_high = int(n_cases * 0.30)
    n_medium = int(n_cases * 0.25)
    n_complicated = int(n_cases * 0.25)
    n_low = n_cases - n_high - n_medium - n_complicated
    
    case_id = 1
    
    # Generate high risk cases
    for _ in range(n_high):
        cases.append(generate_high_risk_case(case_id))
        case_id += 1
    
    # Generate medium risk cases
    for _ in range(n_medium):
        cases.append(generate_medium_risk_case(case_id))
        case_id += 1
    
    # Generate complicated cases
    for _ in range(n_complicated):
        cases.append(generate_complicated_case(case_id))
        case_id += 1
    
    # Generate low risk cases
    for _ in range(n_low):
        cases.append(generate_low_risk_case(case_id))
        case_id += 1
    
    # Shuffle to mix risk levels
    random.shuffle(cases)
    
    return cases


def save_to_csv(cases: List[Dict], filename: str = "generated_test_cases.csv"):
    """บันทึกเป็น CSV"""
    if not cases:
        print("No cases to save!")
        return
    
    # Save to same directory as script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    fieldnames = cases[0].keys()
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for case in cases:
            # Convert list to comma-separated string for CSV (so parser can split it back)
            if isinstance(case.get('other_symptoms'), list):
                case['other_symptoms'] = ', '.join(case['other_symptoms'])
            writer.writerow(case)
    
    print(f"✅ Generated {len(cases)} test cases")
    print(f"📁 Saved to: {filename}")
    
    # Print summary
    risk_counts = {}
    for case in cases:
        risk = case['expected_risk_level']
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    print("\n📊 Risk Level Distribution:")
    for risk, count in sorted(risk_counts.items()):
        print(f"   {risk}: {count} cases ({count/len(cases)*100:.1f}%)")


if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    
    print("🔄 Generating 100 test cases...")
    cases = generate_test_cases(100)
    
    save_to_csv(cases, "generated_test_cases.csv")
    
    print("\n✨ Done! You can now use this data for evaluation.")
    print("Next step: python evaluate_summary.py")
