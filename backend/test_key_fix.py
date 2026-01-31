"""Test key fixes for field mismatches"""

import sys
sys.path.insert(0, '/Users/ohmmy3847/Documents/work/Senior_Project/backend')

from app.services.flow_parser import RuleEngine

def test_compress_key():
    """Test compress_type key"""
    engine = RuleEngine()
    
    # Test with correct key: compress_type
    data = {'compress_type': 'ประคบเย็นอยู่'}
    result = engine.evaluate_compress(data)
    print(f"✅ compress_type='ประคบเย็นอยู่' -> {result}")
    assert result['risk_level'] != 'ไม่สามารถประเมินได้', f"Failed: {result}"
    
    data = {'compress_type': 'ประคบอุ่นอยู่'}
    result = engine.evaluate_compress(data)
    print(f"✅ compress_type='ประคบอุ่นอยู่' -> {result}")
    assert result['risk_level'] != 'ไม่สามารถประเมินได้', f"Failed: {result}"
    
    data = {'compress_type': 'ไม่ได้ประคบอะไรเลย'}
    result = engine.evaluate_compress(data)
    print(f"✅ compress_type='ไม่ได้ประคบอะไรเลย' -> {result}")
    assert result['risk_level'] != 'ไม่สามารถประเมินได้', f"Failed: {result}"

def test_numbness_key():
    """Test numbness_status key"""
    engine = RuleEngine()
    
    data = {'numbness_status': 'หายชาแล้วหลังทำหัตถการ'}
    result = engine.evaluate_numbness(data)
    print(f"✅ numbness_status='หายชาแล้ว' -> {result}")
    assert result['risk_level'] != 'ไม่สามารถประเมินได้', f"Failed: {result}"

def test_walking_key():
    """Test walking_status key"""
    engine = RuleEngine()
    
    data = {'walking_status': 'เดินได้ปกติ'}
    result = engine.evaluate_walking(data)
    print(f"✅ walking_status='เดินได้ปกติ' -> {result}")
    assert result['risk_level'] != 'ไม่สามารถประเมินได้', f"Failed: {result}"

def test_brushing_key():
    """Test brushing_teeth key"""
    engine = RuleEngine()
    
    data = {'brushing_teeth': 'แปรงฟันได้'}
    result = engine.evaluate_brushing(data)
    print(f"✅ brushing_teeth='แปรงฟันได้' -> {result}")
    assert result['risk_level'] != 'ไม่สามารถประเมินได้', f"Failed: {result}"

def test_rinsing_key():
    """Test mouth_rinsing key"""
    engine = RuleEngine()
    
    data = {'mouth_rinsing': 'บ้วนปากได้'}
    result = engine.evaluate_rinsing(data)
    print(f"✅ mouth_rinsing='บ้วนปากได้' -> {result}")
    assert result['risk_level'] != 'ไม่สามารถประเมินได้', f"Failed: {result}"

if __name__ == "__main__":
    print("Testing key fixes...\n")
    
    print("1. Testing compress_type:")
    test_compress_key()
    print()
    
    print("2. Testing numbness_status:")
    test_numbness_key()
    print()
    
    print("3. Testing walking_status:")
    test_walking_key()
    print()
    
    print("4. Testing brushing_teeth:")
    test_brushing_key()
    print()
    
    print("5. Testing mouth_rinsing:")
    test_rinsing_key()
    print()
    
    print("✅ All key fixes working correctly!")
