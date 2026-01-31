"""
Test Rule Parser
"""
from app.services.flow_parser import RuleEngine

# Initialize rule engine
engine = RuleEngine()

# Test case 1: Pain score = 0
print("=" * 60)
print("Test 1: Pain score = 0 (ควรได้ ความเสี่ยงต่ำ)")
print("=" * 60)
result = engine.evaluate_flow("อาการปวด", {
    "pain_score": 0
})
print(f"Risk Level: {result['risk_level']}")
print(f"Reason: {result['reason']}")
print(f"Recommendation: {result['recommendation']}")
print()

# Test case 2: Pain score >= 7
print("=" * 60)
print("Test 2: Pain score >= 7 (ควรได้ ความเสี่ยงสูง)")
print("=" * 60)
result = engine.evaluate_flow("อาการปวด", {
    "pain_score": 8
})
print(f"Risk Level: {result['risk_level']}")
print(f"Reason: {result['reason']}")
print()

# Test case 3: Pain score < 7, medication works
print("=" * 60)
print("Test 3: Pain score < 7, ทานยาแล้วดีขึ้น (ควรได้ ความเสี่ยงต่ำ)")
print("=" * 60)
result = engine.evaluate_flow("อาการปวด", {
    "pain_score": 5,
    "pain_medication_effective": "ดีขึ้น"
})
print(f"Risk Level: {result['risk_level']}")
print(f"Reason: {result['reason']}")
print()

# Test case 4: Pain score < 7, medication doesn't work
print("=" * 60)
print("Test 4: Pain score < 7, ทานยาแล้วไม่ดีขึ้น (ควรได้ ความเสี่ยงสูง)")
print("=" * 60)
result = engine.evaluate_flow("อาการปวด", {
    "pain_score": 5,
    "pain_medication_effective": "ไม่ดีขึ้น"  # แก้เป็น ไม่ดีขึ้น
})
print(f"Risk Level: {result['risk_level']}")
print(f"Reason: {result['reason']}")
print(f"Recommendation: {result['recommendation']}")
print()

# Test case 5: Swelling - breathing difficulty
print("=" * 60)
print("Test 5: มีอาการหายใจลำบาก (ควรได้ ความเสี่ยงสูง)")
print("=" * 60)
result = engine.evaluate_flow("อาการบวม", {
    "breathing_or_swallowing_difficulty": "มี",
    "swelling_status": "บวมมากขึ้น"
})
print(f"Risk Level: {result['risk_level']}")
print(f"Reason: {result['reason']}")
print()

# Test case 6: Swelling - recovered
print("=" * 60)
print("Test 6: หายบวมแล้ว (ควรได้ ข้อมูลไม่เพียงพอในการประเมิน)")
print("=" * 60)
result = engine.evaluate_flow("อาการบวม", {
    # "breathing_or_swallowing_difficulty": None,
    "swelling_status": "ปัจจุบันหายบวมแล้ว"
})
print(f"Risk Level: {result['risk_level']}")
print(f"Reason: {result['reason']}")
print()
