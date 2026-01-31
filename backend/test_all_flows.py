#!/usr/bin/env python3
"""
Comprehensive test suite for all 18 flows
"""

from app.services.flow_parser import RuleEngine

def print_result(test_name, result):
    print("=" * 70)
    print(f"Test: {test_name}")
    print("=" * 70)
    print(f"Risk Level: {result['risk_level']}")
    print(f"Reason: {result['reason']}")
    print(f"Recommendation: {result['recommendation']}")
    print()

def test_all_flows():
    engine = RuleEngine()
    
    print("\n" + "🧪" * 35)
    print("Testing All 18 Flows")
    print("🧪" * 35 + "\n")
    
    # 1. อาการปวด
    print("\n📌 Flow 1: อาการปวด")
    print_result(
        "Pain score = 0",
        engine.evaluate_flow("อาการปวด", {"pain_score": 0})
    )
    print_result(
        "Pain score >= 7",
        engine.evaluate_flow("อาการปวด", {"pain_score": 8})
    )
    print_result(
        "Pain < 7, med works",
        engine.evaluate_flow("อาการปวด", {"pain_score": 4, "pain_medication_effective": "ดีขึ้น"})
    )
    print_result(
        "Pain < 7, med doesn't work",
        engine.evaluate_flow("อาการปวด", {"pain_score": 5, "pain_medication_effective": "ไม่ดีขึ้น"})
    )
    
    # 2. อาการบวม
    print("\n📌 Flow 2: อาการบวม")
    print_result(
        "Breathing difficulty",
        engine.evaluate_flow("อาการบวม", {"breathing_or_swallowing_difficulty": "มีอาการหายใจลำบาก"})
    )
    print_result(
        "Swelling worse, affects life",
        engine.evaluate_flow("อาการบวม", {"swelling_status": "บวมมากขึ้นมากๆจนกระทบการใช้ชีวิต"})
    )
    print_result(
        "Swelling improving",
        engine.evaluate_flow("อาการบวม", {"swelling_status": "บวมน้อยลง"})
    )
    print_result(
        "Swelling resolved",
        engine.evaluate_flow("อาการบวม", {"swelling_status": "หายบวมแล้ว"})
    )
    
    # 3. อาการเลือดออก
    print("\n📌 Flow 3: อาการเลือดออก")
    print_result(
        "No bleeding",
        engine.evaluate_flow("อาการเลือดออก", {"bleeding_status": "ไม่มีเลือดซึมหรือไหลแล้ว"})
    )
    print_result(
        "Minor bleeding, stops",
        engine.evaluate_flow("อาการเลือดออก", {"bleeding_status": "เลือดซึมแต่หยุดได้เอง"})
    )
    print_result(
        "Heavy bleeding",
        engine.evaluate_flow("อาการเลือดออก", {"bleeding_status": "เลือดสีแดงสดไหลไม่หยุดปริมาณมาก"})
    )
    
    # 4. อาการไข้
    print("\n📌 Flow 4: อาการไข้")
    print_result(
        "No fever",
        engine.evaluate_flow("อาการไข้", {"fever_status": "ไม่มีไข้"})
    )
    print_result(
        "Has fever",
        engine.evaluate_flow("อาการไข้", {"fever_status": "มีไข้ (มากกว่า 38 องศาเซลเซียส)"})
    )
    
    # 5. ชา
    print("\n📌 Flow 5: ชา (Numbness)")
    print_result(
        "No numbness",
        engine.evaluate_flow("ชา", {"numbness": "ไม่ชา"})
    )
    print_result(
        "Has numbness",
        engine.evaluate_flow("ชา", {"numbness": "ชา"})
    )
    
    # 6. Phlebitis
    print("\n📌 Flow 6: Phlebitis")
    print_result(
        "No phlebitis",
        engine.evaluate_flow("บริเวณที่เอาเข็มน้ำเกลือออกที่หลังมือหรือข้อมือ (phlebitis)", 
                           {"phlebitis": "ไม่มีอาการปวด/บวม/แดง รอบรอยเข็ม"})
    )
    print_result(
        "Has phlebitis",
        engine.evaluate_flow("บริเวณที่เอาเข็มน้ำเกลือออกที่หลังมือหรือข้อมือ (phlebitis)", 
                           {"phlebitis": "มีอาการปวด/บวม/แดง รอบรอยเข็ม"})
    )
    
    # 7. ไหมเย็บแผล
    print("\n📌 Flow 7: ไหมเย็บแผล")
    print_result(
        "Suture intact",
        engine.evaluate_flow("ไหมเย็บแผล", {"suture_status": "ไหมแน่นดี"})
    )
    print_result(
        "Suture loose, no bleeding",
        engine.evaluate_flow("ไหมเย็บแผล", {"suture_status": "ไหมหลุดหายไปบางส่วน แต่ไม่มีเลือดไหล"})
    )
    print_result(
        "Suture loose with bleeding",
        engine.evaluate_flow("ไหมเย็บแผล", {"suture_status": "ไหมหลุดหายไปบางส่วน และมีอาการเลือดสีแดงสดไหล"})
    )
    
    # 8. อาการอื่นๆ
    print("\n📌 Flow 8: อาการอื่นๆ")
    print_result(
        "High risk symptom",
        engine.evaluate_flow("อาการอื่นๆ (เลือกได้หลายคำตอบ)", 
                           {"other_symptoms": ["ปวดหน่วงบริเวณหน้าแก้ม", "น้ำมูกสีเหลือง"]})
    )
    print_result(
        "Medium risk symptom",
        engine.evaluate_flow("อาการอื่นๆ (เลือกได้หลายคำตอบ)", 
                           {"other_symptoms": ["คัดแน่นจมูก"]})
    )
    print_result(
        "Low risk symptom",
        engine.evaluate_flow("อาการอื่นๆ (เลือกได้หลายคำตอบ)", 
                           {"other_symptoms": ["ช้ำ", "มีน้ำมูก"]})
    )
    
    # 9. ยาปฏิชีวนะ
    print("\n📌 Flow 9: ยาปฏิชีวนะ")
    print_result(
        "Full compliance",
        engine.evaluate_flow("รับประทานยาฆ่าเชื้อครบตามแผนการรักษาหรือไม่?", 
                           {"antibiotic_compliance": "ครบทุกเม็ด"})
    )
    print_result(
        "Sometimes forgot",
        engine.evaluate_flow("รับประทานยาฆ่าเชื้อครบตามแผนการรักษาหรือไม่?", 
                           {"antibiotic_compliance": "ลืมทานบางครั้ง"})
    )
    print_result(
        "No compliance",
        engine.evaluate_flow("รับประทานยาฆ่าเชื้อครบตามแผนการรักษาหรือไม่?", 
                           {"antibiotic_compliance": "ไม่ได้ทานเลย"})
    )
    
    # 10. ประคบ
    print("\n📌 Flow 10: ประคบ")
    print_result(
        "Cold compress",
        engine.evaluate_flow("ประคบเย็น หรือ อุ่นอยู่หรือไม่?", 
                           {"compress": "ประคบเย็นอยู่"})
    )
    print_result(
        "Warm compress",
        engine.evaluate_flow("ประคบเย็น หรือ อุ่นอยู่หรือไม่?", 
                           {"compress": "ประคบอุ่นอยู่"})
    )
    print_result(
        "No compress",
        engine.evaluate_flow("ประคบเย็น หรือ อุ่นอยู่หรือไม่?", 
                           {"compress": "ไม่ได้ประคบอะไรเลย"})
    )
    
    # 11. IMF
    print("\n📌 Flow 11: IMF (การมัดฟัน)")
    print_result(
        "No IMF",
        engine.evaluate_flow("IMF", {"has_imf": "ไม่มี"})
    )
    print_result(
        "IMF tight",
        engine.evaluate_flow("IMF", {"has_imf": "มี", "imf_wire_status": "ลวด/ยางมัดฟันแน่นดี"})
    )
    print_result(
        "IMF loose",
        engine.evaluate_flow("IMF", {"has_imf": "มี", "imf_wire_status": "ลวดมัดฟันหลวม อ้าปากได้เล็กน้อย"})
    )
    
    # 12. แผลสะโพก
    print("\n📌 Flow 12: แผลบริเวณสะโพก")
    print_result(
        "Wound healed",
        engine.evaluate_flow("แผลบริเวณสะโพก: การรักษาการแหว่งของสันเหงือกโดยการนำกระดูกสะโพกมาปลูก", 
                           {"hip_wound": "แผลแห้งดี"})
    )
    print_result(
        "Wound not healed",
        engine.evaluate_flow("แผลบริเวณสะโพก: การรักษาการแหว่งของสันเหงือกโดยการนำกระดูกสะโพกมาปลูก", 
                           {"hip_wound": "แผลยังไม่แห้ง"})
    )
    print_result(
        "Wound infected",
        engine.evaluate_flow("แผลบริเวณสะโพก: การรักษาการแหว่งของสันเหงือกโดยการนำกระดูกสะโพกมาปลูก", 
                           {"hip_wound": "แผลยังไม่แห้ง ร่วมกับมีอาการบวม/แดง/มีหนอง"})
    )
    
    # 13. การเดิน
    print("\n📌 Flow 13: การเดิน")
    print_result(
        "Walking normal",
        engine.evaluate_flow("การเดิน: การรักษาการแหว่งของสันเหงือกโดยการนำกระดูกสะโพกมาปลูก", 
                           {"walking": "เดินได้คล่อง"})
    )
    print_result(
        "Walking difficult",
        engine.evaluate_flow("การเดิน: การรักษาการแหว่งของสันเหงือกโดยการนำกระดูกสะโพกมาปลูก", 
                           {"walking": "เดินไม่ถนัด"})
    )
    
    # 14. การแปรงฟัน
    print("\n📌 Flow 14: การแปรงฟัน")
    print_result(
        "Can brush",
        engine.evaluate_flow("การแปรงฟัน", {"brushing": "แปรงได้"})
    )
    print_result(
        "Cannot brush",
        engine.evaluate_flow("การแปรงฟัน", {"brushing": "แปรงไม่ได้"})
    )
    
    # 15. การบ้วนปาก
    print("\n📌 Flow 15: การบ้วนปาก")
    print_result(
        "Can rinse",
        engine.evaluate_flow("การบ้วนปาก", {"rinsing": "บ้วนได้"})
    )
    print_result(
        "Cannot rinse",
        engine.evaluate_flow("การบ้วนปาก", {"rinsing": "บ้วนไม่ได้"})
    )
    print_result(
        "Not rinsing",
        engine.evaluate_flow("การบ้วนปาก", {"rinsing": "ไม่ได้บ้วน"})
    )
    
    # 16. การกิน
    print("\n📌 Flow 16: วิธีการรับประทานอาหาร")
    print_result(
        "Syringe feeding",
        engine.evaluate_flow("วิธีการรับประทานอาหาร", {"feeding_method": "กระบอกฉีดยา syringe"})
    )
    print_result(
        "NG tube feeding",
        engine.evaluate_flow("วิธีการรับประทานอาหาร", {"feeding_method": "สายยาง nasogastric tube"})
    )
    print_result(
        "Normal feeding",
        engine.evaluate_flow("วิธีการรับประทานอาหาร", {"feeding_method": "รับประทานอาหารได้ปกติ"})
    )
    
    # 17. ประเภทอาหาร
    print("\n📌 Flow 17: ประเภทอาหารที่ทาน")
    print_result(
        "Liquid diet",
        engine.evaluate_flow("ประเภทอาหารที่ทาน (สามารถเลือกได้หลายคำตอบ)", 
                           {"food_types": ["อาหารเหลวใสไม่มีกาก เช่น น้ำซุปใส น้ำผลไม้กรอง นม"]})
    )
    print_result(
        "Soft diet",
        engine.evaluate_flow("ประเภทอาหารที่ทาน (สามารถเลือกได้หลายคำตอบ)", 
                           {"food_types": ["อาหารอ่อน เช่น โจ๊ก ข้าวต้ม ไข่ลวก ผักนึ่ง"]})
    )
    
    # 18. ปริมาณอาหาร
    print("\n📌 Flow 18: ปริมาณอาหารที่ทาน")
    print_result(
        "Normal amount",
        engine.evaluate_flow("ปริมาณอาหารที่ทาน", {"food_amount": "รับประทานอาหารปริมาณปกติ"})
    )
    print_result(
        "Reduced amount",
        engine.evaluate_flow("ปริมาณอาหารที่ทาน", {"food_amount": "รับประทานอาหารได้น้อยลง"})
    )
    
    # 19. NG Tube Position
    print("\n📌 Flow 19: ตำแหน่งสายยางให้อาหาร (NG tube)")
    print_result(
        "NG tube in position",
        engine.evaluate_flow("ตำแหน่งสายยางให้อาหาร: กรณีในผู้ป่วยที่รับประทานอาหารผ่านทางสายยาง (on NG-nasogastric tube)", 
                           {"ng_tube_position": "สายยางอยู่ในตำแหน่งเดิม เทปยึดจมูกกับสายแน่นดี"})
    )
    print_result(
        "NG tube displaced",
        engine.evaluate_flow("ตำแหน่งสายยางให้อาหาร: กรณีในผู้ป่วยที่รับประทานอาหารผ่านทางสายยาง (on NG-nasogastric tube)", 
                           {"ng_tube_position": "สายยางเลื่อนตำแหน่ง เทปยึดจมูกกับสายไม่แน่น"})
    )
    
    print("\n" + "✅" * 35)
    print("All Tests Completed!")
    print("✅" * 35 + "\n")

if __name__ == '__main__':
    test_all_flows()
