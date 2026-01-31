#!/usr/bin/env python3
"""Test API call to debug 422 error"""
import requests
import json

payload = {
    "basic_info": {
        "first_name": "ทดสอบ",
        "last_name": "001",
        "age": 25,
        "gender": "ชาย",
        "procedures": ["Orthognathic surgery"]
    },
    "assessment_data": {
        "pain_score": 5,
        "pain_medication_effect": "ดีขึ้น",
        "swelling_status": "บวมเท่าเดิม",
        "breathing_or_swallowing_difficulty": "ไม่มี",
        "compress_type": "ประคบเย็นอยู่",
        "brushing_teeth": "แปรงฟันได้",
        "mouth_rinsing": "บ้วนปากได้",
        "feeding_method": "รับประทานอาหารได้ปกติ"
    }
}

print("Sending payload:")
print(json.dumps(payload, indent=2, ensure_ascii=False))
print("\n" + "="*60)

try:
    response = requests.post(
        "http://localhost:8000/patient-assessment",
        json=payload,
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 422:
        print("\nValidation Error Details:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
