"""
Constants and Field Mappings for Patient Assessment System

This module contains all shared constants used across the application:
- Field labels (Thai names for form fields)
- Field mappings (relationships between fields)
- Custom text field definitions
"""

# ------------------------------------------------------------
# Field Label Mappings
# ------------------------------------------------------------
PHONE_NUMBER = '02-2188750'
# Mapping ระหว่าง field name กับชื่อคำถามที่อ่านง่าย
FIELD_LABELS = {
    # Basic Info (ข้อ 1-5)
    'age': 'อายุ',
    'gender': 'เพศ',
    'hn': 'HN',
    'procedures': 'หัตถการที่ทำ',
    'surgery_date': 'ได้รับการผ่าตัดเมื่อวันที่',
    'note': 'หมายเหตุพิเศษ (สำหรับหมอ)',
    
    # Symptoms (ข้อ 6-20)
    'pain_score': 'ระดับความปวด (Pain score)',
    'pain_medication_effective': 'ทานยาแก้ปวดแล้วดีขึ้นหรือไม่',
    'swelling_status': 'อาการบวม',
    'breathing_or_swallowing_difficulty': 'มีอาการหายใจลำบาก หรือ กลืนลำบากหรือไม่',
    'bleeding_status': 'อาการเลือดซึม หรือ เลือดออก',
    'fever_status': 'อาการไข้',
    'numbness_status': 'อาการชา',
    'phlebitis': 'บริเวณที่เอาเข็มน้ำเกลือออก',
    'suture_status': 'ไหมเย็บแผล',
    'other_symptoms': 'อาการอื่นๆ',
    'other_symptoms_custom': 'อาการอื่นๆที่ผู้ป่วยระบุเพิ่มเติม',
    'antibiotic_compliance': 'รับประทานยาฆ่าเชื้อ',
    'compress_type': 'ประคบเย็น หรือ อุ่นอยู่หรือไม่',
    'has_imf': 'มีการมัดฟันบนและล่างเข้าด้วยกัน (IMF)',
    'imf_wire_status': 'ลวด/ยางมัดฟันแน่นดีหรือไม่',
    'walking_status': 'การเดิน',
    
    # Daily Life (ข้อ 21-27)
    'brushing_teeth': 'การแปรงฟัน',
    'mouth_rinsing': 'การบ้วนปาก',
    'feeding_method': 'วิธีการรับประทานอาหาร',
    'food_types': 'ประเภทอาหารที่ทาน',
    'food_types_custom': 'ประเภทอาหารที่ผู้ป่วยระบุเพิ่มเติม',
    'food_amount': 'ปริมาณอาหารที่ทาน',
    'additional_questions': 'ผู้ป่วยมีคำถามที่จะสอบถามพยาบาลเพิ่มเติม',
    'ng_tube_position': 'ตำแหน่งสายยางให้อาหาร',
}

# FORM_COLUMNS includes Timestamp as first column (matches Google Sheets structure)
FORM_COLUMNS = ['Timestamp'] + list(FIELD_LABELS.values())


# ------------------------------------------------------------
# Field Relationship Mappings
# ------------------------------------------------------------

# Mapping ระหว่าง main field กับ description field
FIELD_WITH_DESCRIPTION = {
    'swelling_status': 'swelling_description',
    'breathing_or_swallowing_difficulty': 'breathing_description',
    'bleeding_status': 'bleeding_description',
    'fever_status': 'fever_description',
    'numbness_status': 'numbness_description',
    'phlebitis': 'phlebitis_description',
    'suture_status': 'suture_description',
    'antibiotic_compliance': 'antibiotic_description',
    'imf_wire_status': 'imf_wire_description',
    'walking_status': 'walking_description',
    'brushing_teeth': 'brushing_description',
    'mouth_rinsing': 'rinsing_description',
    'feeding_method': 'feeding_description',
    'food_amount': 'food_amount_description',
    'ng_tube_position': 'ng_tube_description',
}

# Mapping ชื่อ description field ที่อ่านง่าย
DESCRIPTION_LABELS = {
    'swelling_description': 'คำอธิบายเพิ่มเติมสำหรับอาการบวม',
    'breathing_description': 'คำอธิบายเพิ่มเติมสำหรับอาการหายใจ/กลืนลำบาก',
    'bleeding_description': 'คำอธิบายเพิ่มเติมสำหรับอาการเลือดซึม/เลือดออก',
    'fever_description': 'คำอธิบายเพิ่มเติมสำหรับอาการไข้',
    'numbness_description': 'คำอธิบายเพิ่มเติมสำหรับอาการชา',
    'phlebitis_description': 'คำอธิบายเพิ่มเติมสำหรับบริเวณเข็มน้ำเกลือ',
    'suture_description': 'คำอธิบายเพิ่มเติมสำหรับไหมเย็บแผล',
    'antibiotic_description': 'จำนวนครั้งที่ลืมทานยาฆ่าเชื้อ (Antibiotic)',
    'imf_wire_description': 'คำอธิบายเพิ่มเติมสำหรับลวด/ยางมัดฟัน',
    'walking_description': 'คำอธิบายเพิ่มเติมสำหรับการเดิน',
    'brushing_description': 'คำอธิบายเพิ่มเติมสำหรับการแปรงฟัน',
    'rinsing_description': 'คำอธิบายเพิ่มเติมสำหรับการบ้วนปาก',
    'feeding_description': 'คำอธิบายเพิ่มเติมสำหรับวิธีการรับประทานอาหาร',
    'food_amount_description': 'คำอธิบายเพิ่มเติมสำหรับปริมาณอาหาร',
    'ng_tube_description': 'คำอธิบายเพิ่มเติมสำหรับตำแหน่งสายยางให้อาหาร',
}


# ------------------------------------------------------------
# Custom Text Field Definitions
# ------------------------------------------------------------

# Custom text fields that contain free text entered by patient
# These will be analyzed by LLM for additional risk assessment
# Frontend sends these as arrays (string[]) of custom values
CUSTOM_TEXT_FIELDS = {
    'other_symptoms_custom': 'อาการอื่นๆที่ผู้ป่วยระบุเพิ่มเติม',
    'food_types_custom': 'ประเภทอาหารที่ผู้ป่วยระบุเพิ่มเติม',
}


# ------------------------------------------------------------
# Flow Topic Names (ย้ายมาจาก risk_service.py)
# ------------------------------------------------------------
# key = flow_name จริงๆ ที่ RuleEngine ส่งมา (ดูจาก evaluators dict ใน flow_parser.py)
# แก้ค่า 'th' / 'en' เพื่อเปลี่ยนชื่อที่แสดง
FLOW_TOPIC_NAMES: dict[str, dict[str, str]] = {
    # ── Flow ปกติ ──────────────────────────────────────────────────────────
    'pain':                 {'th': 'อาการปวด',      'en': 'Pain'},
    'swelling':             {'th': 'อาการบวม',      'en': 'Swelling'},
    'bleeding':             {'th': 'เลือดออก',      'en': 'Bleeding'},
    'fever':                {'th': 'ไข้',           'en': 'Fever'},
    'numbness':             {'th': 'อาการชา',       'en': 'Numbness'},
    'phlebitis':            {'th': 'บริเวณที่เอาเข็มน้ำเกลือออกที่หลังมือหรือข้อมือ',   'en': 'phlebitis at needle site'},
    'suture':               {'th': 'ไหมเย็บแผล',    'en': 'Suture'},
    'other_symptoms':       {'th': 'อาการอื่นๆ',    'en': 'Other Symptoms'},
    'antibiotics_compliance': {'th': 'ยาฆ่าเชื้อ',    'en': 'Antibiotics'},
    'compress':             {'th': 'การประคบ',      'en': 'Compress'},
    'imf_wire':             {'th': 'ลวดมัดฟัน',     'en': 'IMF Wire'},
    'walking':              {'th': 'การเดิน',       'en': 'Walking'},
    'ng_tube':              {'th': 'สายให้อาหาร',   'en': 'NG Tube'},
    'brushing':             {'th': 'การแปรงฟัน',    'en': 'Brushing'},
    'rinsing':              {'th': 'การบ้วนปาก',    'en': 'Rinsing'},
    'food_type':            {'th': 'ประเภทอาหาร',   'en': 'Food Type'},
    'food_intake':          {'th': 'ปริมาณอาหาร',   'en': 'Food Intake'},

    # ── อาการอื่นๆ (key = symptom key จาก symptom_map ใน flow_parser.py) ──
    'sinus_pain':       {'th': 'ปวดหน้าแก้ม',     'en': 'Sinus Pain'},
    'nausea_vomiting':  {'th': 'คลื่นไส้/อาเจียน', 'en': 'Nausea/Vomiting'},
    'cough':            {'th': 'ไอ/เสมหะ',         'en': 'Cough'},
    'stuffy_nose':      {'th': 'คัดจมูก',           'en': 'Stuffy Nose'},
    'bruising':         {'th': 'รอยช้ำ',            'en': 'Bruising'},
    'diarrhea':         {'th': 'ท้องเสีย',          'en': 'Diarrhea'},
    'runny_nose':       {'th': 'น้ำมูก',            'en': 'Runny Nose'},
    'sore_throat':      {'th': 'เจ็บคอ',            'en': 'Sore Throat'},
    'weight_loss':      {'th': 'น้ำหนักลด',         'en': 'Weight Loss'},
    'headache':         {'th': 'ปวดหัว',            'en': 'Headache'},
}


