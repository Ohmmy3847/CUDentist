"""
ตัวอย่าง Patient Data สำหรับทดสอบ Assessment API
ใช้ตัวเลือกจาก frontend/lib/types/form.types.ts

⚠️  สำคัญ: Request Format ใหม่ (แยก Basic Info และ Assessment Data)
    {
        "basic_info": {
            // Personal Information
            "first_name": "...",
            "last_name": "...",
            "email": "...",
            "phone": "...",
            "birth_year": 2540,
            // Basic Medical Info
            "age": 25,
            "gender": "ชาย",
            "hn": "HN12345",
            "procedures": ["BSSRO"],
            "surgery_date": "2026-01-09",
            "discharge_date": "2026-01-10",
            "note": "...",
            // Special Procedures
            "has_imf": "มีการมัดฟัน",
            "imf_type": "มัดยาง",
            ...
        },
        "assessment_data": {
            // Symptoms and Care
            "pain_score": 5,
            "pain_medication_effect": "ดีขึ้น",
            "swelling_status": "บวมมาก",
            "bleeding_status": "ไม่มีเลือดซึม",
            "additional_questions": "...",
            ...
        }
    }

Usage:
    python test_assessment_examples.py

หรือ import ไปใช้:
    from test_assessment_examples import SAMPLE_DATA_HIGH_RISK, SAMPLE_DATA_LOW_RISK
"""

import requests
import json

# ============================================================
# ตัวอย่างที่ 1: ผู้ป่วยความเสี่ยงสูง
# กรณีที่สมจริง: มีอาการแทรกซ้อนร้ายแรง 1 อาการ (เลือดออกไม่หยุด)
# ส่วนอาการอื่นๆ เป็นปกติหรือเล็กน้อย
# ============================================================
SAMPLE_DATA_HIGH_RISK = {
    "basic_info": {
        "first_name": "สมชาย",
        "last_name": "ใจดี",
        "email": "somchai@example.com",
        "phone": "0812345678",
        "birth_year": 2534,
        
        "age": 35,
        "gender": "ชาย",
        "hn": "HN12345678",
        "procedures": ["ผ่าตัดขากรรไกรล่าง (BSSRO-bilateral sagittal split osteotomy)"],
        "lefort_sub_options": [],
        "bssro_sub_options": ["setback"],
        "surgery_date": "2026-01-09",
        "discharge_date": "2026-01-10",
        "note": "",
        
       
        "has_imf": "มีการมัดฟัน",
        "imf_type": "มัดยาง",
        "imf_loops": 2,
        "special_icbg": "ไม่ทำ",
        "special_ng_tube": "ไม่ทำ"
    },
    
    "assessment_data": {
        
        
        "pain_score": 3,
        "pain_medication_effect": "ดีขึ้น",
        
        "swelling_status": "บวมเท่าเดิม",
        "swelling_description": "บวมบริเวณแก้มปกติหลังผ่าตัด",
        
        "breathing_or_swallowing_difficulty": "ไม่มี",
        "breathing_description": "",
        
        "bleeding_status": "เลือดสีแดงสดไหลไม่หยุดปริมาณมาก",
        "bleeding_description": "มีเลือดออกจากแผลในปากทางด้านซ้ายไหลต่อเนื่อง กัดผ้าก๊อซแล้วแต่ยังไม่หยุด",
        
        "fever_status": "ไม่มีไข้",
        "fever_description": "",
        
        "numbness_status": "ยังชาอยู่แต่ชาน้อยลงเรื่อยๆ",
        "numbness_description": "ชาบริเวณริมฝีปากล่างเล็กน้อย ดีขึ้นทุกวัน",
        
        "phlebitis": "ไม่มีอาการปวด/บวม/แดง รอบรอยเข็ม",
        "phlebitis_description": "",
        
        "suture_status": "ไหมแน่นดี / ไม่ได้สังเกต",
        "suture_description": "",
        
        "other_symptoms": [],
        "other_symptoms_custom": [],
        
       
        "antibiotic_compliance": "ครบตามแพทย์สั่ง",
        "antibiotic_description": "",
        
        "compress_type": "ประคบเย็นอยู่",
        
       
        "imf_wire_status": "ลวด/ยางมัดฟันแน่นดี",
        "imf_wire_description": "",
        
        "brushing_teeth": "แปรงฟันได้",
        "brushing_description": "แปรงฟันนุ่มๆ ระมัดระวัง",
        
        "mouth_rinsing": "บ้วนปากได้",
        "rinsing_description": "บ้วนปากด้วยน้ำเกลือได้",
        
        "feeding_method": "รับประทานอาหารผ่านกระบอกฉีดยา (syringe)",
        "feeding_description": "ใช้ syringe ดูดอาหารเหลว",
        
        "food_types": ["อาหารเหลวใสไม่มีกาก เช่น น้ำซุปใส น้ำผลไม้กรอง นม"],
        "food_amount": "รับประทานอาหารได้น้อยลง",
        "food_amount_description": "ทานน้ำซุป นมได้ปกติ",
        
        "additional_questions": "เลือดออกจากในปากไม่หยุดสักที กัดผ้าก๊อซแล้วแต่ยังมีเลือดออกอยู่ ควรทำอย่างไร?"
    }
}


# ============================================================
# ตัวอย่างที่ 2: ผู้ป่วยความเสี่ยงกลาง
# กรณีที่สมจริง: มีอาการต้องติดตาม 1 อาการ (บวมมากขึ้น)
# ส่วนอาการอื่นๆ เป็นปกติ
# ============================================================
SAMPLE_DATA_MEDIUM_RISK = {
    "basic_info": {
       
        "first_name": "สมหญิง",
        "last_name": "รักษ์ดี",
        "email": "somying@example.com",
        "phone": "0898765432",
        "birth_year": 2541,
        
     
        "age": 28,
        "gender": "หญิง",
        "hn": "HN87654321",
        "procedures": ["ผ่าตัดขากรรไกรบน  (Lefort I)"],
        "lefort_sub_options": ["advancement"],
        "bssro_sub_options": [],
        "surgery_date": "2026-01-08",
        "discharge_date": "2026-01-09",
        "note": "",
        
       
        "has_imf": "ไม่มีการมัดฟัน"
    },
    
    "assessment_data": {
        
     
        "pain_score": 3,
        "pain_medication_effect": "ดีขึ้น",
        
        
        "swelling_status": "บวมมากขึ้น",
        "swelling_description": "บวมบริเวณแก้มทั้งสองข้างมากขึ้นกว่าเมื่อวาน หน้าตึงกว่าเดิม",
        
        "breathing_or_swallowing_difficulty": "ไม่มี",
        "breathing_description": "",
        
        "bleeding_status": "ไม่มีเลือดซึมหรือไหลแล้ว",
        "bleeding_description": "",
        
        "fever_status": "ไม่มีไข้",
        "fever_description": "",
        
        "numbness_status": "ยังชาอยู่แต่ชาน้อยลงเรื่อยๆ",
        "numbness_description": "ชาบริเวณริมฝีปากล่างเล็กน้อย ดีขึ้นเรื่อยๆ",
        
        "phlebitis": "ไม่มีอาการปวด/บวม/แดง รอบรอยเข็ม",
        "phlebitis_description": "",
        
        "suture_status": "ไหมแน่นดี / ไม่ได้สังเกต",
        "suture_description": "",
        
        "other_symptoms": [],
        "other_symptoms_custom": [],
        
        
        "antibiotic_compliance": "ครบตามแพทย์สั่ง",
        "antibiotic_description": "",
        
        "compress_type": "ประคบเย็นอยู่",
        
        "brushing_teeth": "แปรงฟันได้",
        "brushing_description": "แปรงฟันนุ่มๆ ได้สบาย",
        
        "mouth_rinsing": "บ้วนปากได้",
        "rinsing_description": "บ้วนปากด้วยน้ำเกลือได้ดี",
        
        "feeding_method": "รับประทานอาหารผ่านกระบอกฉีดยา (syringe)",
        "feeding_description": "ใช้ syringe ดูดอาหารเหลวได้สะดวก",
        
        "food_types": ["อาหารเหลวใสไม่มีกาก เช่น น้ำซุปใส น้ำผลไม้กรอง นม"],
        "food_amount": "รับประทานอาหารปริมาณปกติ",
        "food_amount_description": "ทานน้ำซุป น้ำผลไม้ได้ปกติ",
        
        "additional_questions": "หน้าบวมมากขึ้นเรื่อยๆ เป็นปกติหรือเปล่าคะ?"
    }
}


# ============================================================
# ตัวอย่างที่ 3: ผู้ป่วยความเสี่ยงต่ำ
# ============================================================
SAMPLE_DATA_LOW_RISK = {
    "basic_info": {
       
        "first_name": "กัญญา",
        "last_name": "สุขใจ",
        "email": "kanya@example.com",
        "phone": "0891234567",
        "birth_year": 2547,
        

        "age": 22,
        "gender": "หญิง",
        "hn": "HN11223344",
        "procedures": ["ผ่าตัดขากรรไกรล่าง (BSSRO-bilateral sagittal split osteotomy)"],
        "lefort_sub_options": [],
        "bssro_sub_options": ["advancement"],
        "surgery_date": "2026-01-08",
        "discharge_date": "2026-01-09",
        "note": "ผู้ป่วยฟื้นตัวดี ไม่มีภาวะแทรกซ้อน",
        
        
        "has_imf": "ไม่มีการมัดฟัน"
    },
    
    "assessment_data": {
        
      
        "pain_score": 2,
        "pain_medication_effect": "ดีขึ้น",
        
        "swelling_status": "บวมลดลง",
        "swelling_description": "บวมนิดหน่อย คลายลงเรื่อยๆ",
        
        "breathing_or_swallowing_difficulty": "ไม่มี",
        "breathing_description": "",
        
        "bleeding_status": "ไม่มีเลือดซึมหรือไหลแล้ว",
        "bleeding_description": "",
        
        "fever_status": "ไม่มีไข้",
        "fever_description": "",
        
        "numbness_status": "หายชาแล้วหลังทำหัตถการ",
        "numbness_description": "",
        
        "phlebitis": "ไม่มีอาการปวด/บวม/แดง รอบรอยเข็ม",
        "phlebitis_description": "",
        
        "suture_status": "ไหมแน่นดี / ไม่ได้สังเกต",
        "suture_description": "",
        
        "other_symptoms": [],
        "other_symptoms_custom": [],
        
        
        "antibiotic_compliance": "ครบตามแพทย์สั่ง",
        "antibiotic_description": "",
        
        "compress_type": "ประคบอุ่นอยู่",
        
        "brushing_teeth": "แปรงฟันได้",
        "brushing_description": "แปรงฟันนุ่มๆ ได้สบาย",
        
        "mouth_rinsing": "บ้วนปากได้",
        "rinsing_description": "บ้วนปากด้วยน้ำเกลือได้ดี",
        
        "feeding_method": "รับประทานอาหารได้ปกติ",
        "feeding_description": "ทานอาหารปกติได้",
        
        "food_types": [
            "อาหารอ่อน เช่น โจ๊ก ข้าวต้ม ไข่ลวก ผักนึ่ง",
            "อาหารปั่นเหลวมีกาก เช่น โจ๊กปั่นเหลว ไก่ปั่น"
        ],
        "food_amount": "รับประทานอาหารปริมาณปกติ",
        "food_amount_description": "ทานข้าวต้ม โจ๊ก ได้ปกติ",
        
        "additional_questions": ""
    }
}


# ============================================================
# ตัวอย่างที่ 4: ผู้ป่วยกรณี COMPLICATED
# อาการส่วนใหญ่ปกติ (ความเสี่ยงต่ำ) แต่มีอาการอื่นๆที่ผู้ป่วยระบุเพิ่มเติม
# ============================================================
SAMPLE_DATA_COMPLICATED = {
    "basic_info": {
       
        "first_name": "วิชัย",
        "last_name": "มั่นคง",
        "email": "wichai@example.com",
        "phone": "0876543210",
        "birth_year": 2538,
        
      
        "age": 31,
        "gender": "ชาย",
        "hn": "HN99887766",
        "procedures": ["ผ่าตัดขากรรไกรล่าง (BSSRO-bilateral sagittal split osteotomy)"],
        "lefort_sub_options": [],
        "bssro_sub_options": ["setback"],
        "surgery_date": "2026-01-07",
        "discharge_date": "2026-01-08",
        "note": "",
        
       
        "has_imf": "มีการมัดฟัน",
        "imf_type": "มัดยาง",
        "imf_loops": 4,
        "special_icbg": "ไม่ทำ",
        "special_ng_tube": "ไม่ทำ"
    },
    
    "assessment_data": {
        
       
        "pain_score": 2,  
        "pain_medication_effect": "ดีขึ้น",
        
        "swelling_status": "บวมเท่าเดิม", 
        "swelling_description": "บวมบริเวณแก้มปกติหลังผ่าตัด",
        
        "breathing_or_swallowing_difficulty": "ไม่มี", 
        "breathing_description": "",
        
        "bleeding_status": "ไม่มีเลือดซึมหรือไหลแล้ว",  
        "bleeding_description": "",
        
        "fever_status": "ไม่มีไข้",  
        "fever_description": "",
        
        "numbness_status": "ยังชาอยู่แต่ชาน้อยลงเรื่อยๆ",  
        "numbness_description": "ชาบริเวณคางเล็กน้อย",
        
        "phlebitis": "ไม่มีอาการปวด/บวม/แดง รอบรอยเข็ม", 
        "phlebitis_description": "",
        
        "suture_status": "ไหมแน่นดี / ไม่ได้สังเกต",  
        "suture_description": "",
        
        
        "other_symptoms": [],  
        "other_symptoms_custom": ["มีเสียงแปลกๆ ตอนเคลื่อนไหวขากรรไกร", "รู้สึกว่าฟันไม่สบฟัน"],
        
       
        "antibiotic_compliance": "ครบตามแพทย์สั่ง", 
        "antibiotic_description": "",
        
        "compress_type": "ประคบเย็นอยู่",  
        
    
        "imf_wire_status": "ลวด/ยางมัดฟันแน่นดี", 
        "imf_wire_description": "",
        
        "brushing_teeth": "แปรงฟันได้",  
        "brushing_description": "แปรงฟันระมัดระวัง",
        
        "mouth_rinsing": "บ้วนปากได้",  
        "rinsing_description": "บ้วนปากด้วยน้ำเกลือ",
        
        "feeding_method": "รับประทานอาหารผ่านกระบอกฉีดยา (syringe)", 
        "feeding_description": "ใช้ syringe ดูดอาหารเหลว",
        
        "food_types": ["อาหารเหลวใสไม่มีกาก เช่น น้ำซุปใส น้ำผลไม้กรอง นม"],  
        "food_amount": "รับประทานอาหารปริมาณปกติ",  
        "food_amount_description": "ทานน้ำซุป นมได้ปกติ",
        
        "additional_questions": "มีเสียงดังตอนเคลื่อนไหวขากรรไกร และรู้สึกว่าฟันไม่สบฟัน เป็นปกติหรือเปล่าครับ?"
    }
}


# ============================================================
# ฟังก์ชันสำหรับทดสอบ API
# ============================================================
def test_assessment_api(sample_data, api_url="http://localhost:8000/patient-assessment"):
    """
    ทดสอบเรียก Assessment API
    
    Args:
        sample_data: dict ของข้อมูลผู้ป่วย (format: {basic_info: {...}, assessment_data: {...}})
        api_url: URL ของ API endpoint
    """
    try:
        basic_info = sample_data.get('basic_info', {})
        print("=" * 80)
        print(f"📤 ส่งข้อมูล: {basic_info.get('first_name', '')} {basic_info.get('last_name', '')} (HN={basic_info.get('hn', 'N/A')})")
        print("=" * 80)
        
        response = requests.post(
            api_url,
            json=sample_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ สำเร็จ!\n")
            
            # แสดงผลลัพธ์
            print("📊 ผลการประเมิน:")
            print("-" * 80)
            
            if "summary" in result:
                print(f"\n🎯 ความเสี่ยงโดยรวม: {result['summary'].get('overall_risk', 'N/A')}")
                print(f"\n📝 สรุป:\n{result['summary'].get('summary', 'N/A')}")
                
                if result['summary'].get('critical_issues'):
                    print(f"\n⚠️  ปัญหาเร่งด่วน:")
                    for issue in result['summary']['critical_issues']:
                        print(f"   - {issue}")
            
            if "flows" in result:
                print(f"\n📋 รายละเอียดแต่ละด้าน ({len(result['flows'])} ด้าน):")
                for flow_name, flow_result in result['flows'].items():
                    risk = flow_result.get('risk_level', 'N/A')
                    emoji = "🔴" if "สูง" in risk else "🟡" if "กลาง" in risk else "🟢"
                    print(f"   {emoji} {flow_name}: {risk}")
            
            if "patient_qa" in result and result['patient_qa'].get('answer'):
                print(f"\n💬 คำตอบสำหรับคำถาม:")
                print(f"   {result['patient_qa']['answer']}")
            
            print("\n" + "=" * 80)
            return result
            
        else:
            print(f"❌ Error {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        return None


def save_sample_json():
    """บันทึกตัวอย่างเป็นไฟล์ JSON"""
    samples = {
        "high_risk": SAMPLE_DATA_HIGH_RISK,
        "medium_risk": SAMPLE_DATA_MEDIUM_RISK,
        "low_risk": SAMPLE_DATA_LOW_RISK,
        "complicated": SAMPLE_DATA_COMPLICATED
    }
    
    for name, data in samples.items():
        filename = f"sample_{name}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ บันทึก {filename}")


# ============================================================
# Main - ตัวอย่างการใช้งาน
# ============================================================
if __name__ == "__main__":
    print("🏥 ตัวอย่างข้อมูลสำหรับทดสอบ Assessment API\n")
    
    # แสดงตัวเลือก
    print("เลือกตัวอย่างที่ต้องการทดสอบ:")
    print("1. ผู้ป่วยความเสี่ยงสูง (มีอาการแทรกซ้อนหลายอย่าง)")
    print("2. ผู้ป่วยความเสี่ยงกลาง (มีอาการบ้าง ต้องติดตาม)")
    print("3. ผู้ป่วยความเสี่ยงต่ำ (ฟื้นตัวดี)")
    print("4. ผู้ป่วยกรณี COMPLICATED (ปกติ แต่มีอาการแปลกๆ ที่ระบุเพิ่มเติม)")
    print("5. บันทึกทุกตัวอย่างเป็นไฟล์ JSON")
    print("6. ทดสอบทั้งหมด")
    print("7. แสดงตัวอย่าง dict ของแต่ละ case")
    
    choice = input("\nเลือก (1-7): ").strip()
    
    if choice == "1":
        test_assessment_api(SAMPLE_DATA_HIGH_RISK)
    elif choice == "2":
        test_assessment_api(SAMPLE_DATA_MEDIUM_RISK)
    elif choice == "3":
        test_assessment_api(SAMPLE_DATA_LOW_RISK)
    elif choice == "4":
        test_assessment_api(SAMPLE_DATA_COMPLICATED)
    elif choice == "5":
        save_sample_json()
    elif choice == "6":
        print("\n🔄 ทดสอบทั้งหมด...\n")
        test_assessment_api(SAMPLE_DATA_HIGH_RISK)
        print("\n" + "="*80 + "\n")
        test_assessment_api(SAMPLE_DATA_MEDIUM_RISK)
        print("\n" + "="*80 + "\n")
        test_assessment_api(SAMPLE_DATA_LOW_RISK)
        print("\n" + "="*80 + "\n")
        test_assessment_api(SAMPLE_DATA_COMPLICATED)
    elif choice == "7":
        print("\n📋 ตัวอย่าง dict สำหรับแต่ละ case:\n")
        print("=" * 80)
        print("SAMPLE_DATA_HIGH_RISK (ความเสี่ยงสูง):")
        print("=" * 80)
        print(json.dumps(SAMPLE_DATA_HIGH_RISK, ensure_ascii=False, indent=2))
        print("\n" + "=" * 80)
        print("SAMPLE_DATA_MEDIUM_RISK (ความเสี่ยงกลาง):")
        print("=" * 80)
        print(json.dumps(SAMPLE_DATA_MEDIUM_RISK, ensure_ascii=False, indent=2))
        print("\n" + "=" * 80)
        print("SAMPLE_DATA_LOW_RISK (ความเสี่ยงต่ำ):")
        print("=" * 80)
        print(json.dumps(SAMPLE_DATA_LOW_RISK, ensure_ascii=False, indent=2))
        print("\n" + "=" * 80)
        print("SAMPLE_DATA_COMPLICATED (กรณีซับซ้อน):")
        print("=" * 80)
        print(json.dumps(SAMPLE_DATA_COMPLICATED, ensure_ascii=False, indent=2))
    else:
        print("❌ กรุณาเลือก 1-7")
    
    print("\n💡 Tips:")
    print("   - Import: from test_assessment_examples import SAMPLE_DATA_HIGH_RISK, SAMPLE_DATA_COMPLICATED")
    print("   - curl: curl -X POST http://localhost:8000/patient-assessment -H 'Content-Type: application/json' -d @sample_high_risk.json")
    print("   - ตัวเลือกทั้งหมดมาจาก frontend/lib/types/form.types.ts")
