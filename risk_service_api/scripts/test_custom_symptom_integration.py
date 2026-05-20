import asyncio
import httpx
import json
import sys

async def test_assessment():
    async with httpx.AsyncClient() as client:
        payload = {
            "basic_info": {
                "first_name": "สมชาย",
                "last_name": "ใจดี",
                "birth_date": "2000-05-15",
                "hn": "HN12345",
                "procedures": ["BSSRO"],
                "surgery_date": "2026-01-09"
            },
            "assessment_data": {
                "pain_score": 3,
                "pain_medication_effect": "ดีขึ้น",
                "swelling_status": "หายบวมแล้ว",
                "other_symptoms_custom": "แสบคอและมีรอยช้ำสีม่วง",
                "other_symptoms": ["headache"]
            },
            "language": "th"
        }
        
        try:
            response = await client.post(
                "http://127.0.0.1:8000/risk_service_api/patient-assessment",
                json=payload,
                timeout=60.0
            )
            print(f"Status: {response.status_code}")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except Exception as e:
            print("HTTP Request Failed:", str(e))

if __name__ == "__main__":
    asyncio.run(test_assessment())
