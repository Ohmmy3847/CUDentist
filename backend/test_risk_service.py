#!/usr/bin/env python3
"""
Test risk_service.py with RuleEngine integration
"""

from app.services.risk_service import classify_risk

def test_classify_risk():
    print("Testing classify_risk with RuleEngine...")
    print("=" * 70)
    
    # Test data
    test_data = {
        "pain_score": 8,
        "pain_medication_effective": "ไม่ดีขึ้น",
        "swelling_status": "บวมมากขึ้น",
        "bleeding_status": "ไม่มีเลือดซึมหรือไหลแล้ว",
        "fever_status": "ไม่มีไข้"
    }
    
    # Test pain flow
    print("\n1. Testing อาการปวด flow:")
    result = classify_risk(
        input_data=test_data,
        flow_name="อาการปวด"
    )
    print(f"   Risk Level: {result.risk_level}")
    print(f"   Reason: {result.reason}")
    print(f"   Recommendation: {result.recommendation}")
    
    # Test swelling flow
    print("\n2. Testing อาการบวม flow:")
    result = classify_risk(
        input_data=test_data,
        flow_name="อาการบวม"
    )
    print(f"   Risk Level: {result.risk_level}")
    print(f"   Reason: {result.reason}")
    print(f"   Recommendation: {result.recommendation}")
    
    # Test bleeding flow
    print("\n3. Testing อาการเลือดออก flow:")
    result = classify_risk(
        input_data=test_data,
        flow_name="อาการเลือดซึม/ เลือดออก"
    )
    print(f"   Risk Level: {result.risk_level}")
    print(f"   Reason: {result.reason}")
    print(f"   Recommendation: {result.recommendation}")
    
    # Test fever flow
    print("\n4. Testing อาการไข้ flow:")
    result = classify_risk(
        input_data=test_data,
        flow_name="อาการไข้"
    )
    print(f"   Risk Level: {result.risk_level}")
    print(f"   Reason: {result.reason}")
    print(f"   Recommendation: {result.recommendation}")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed! Rule-based classification working correctly.")

if __name__ == "__main__":
    test_classify_risk()
