#!/usr/bin/env python3
"""Test API payload to debug 422 error"""
import requests
import json
import csv
import sys
sys.path.insert(0, '..')
sys.path.insert(0, '../..')

# Load first case
with open('generated_test_cases.csv', 'r') as f:
    reader = csv.DictReader(f)
    case = next(reader)

print("=== Case Data ===")
print(f"case_id: {case.get('case_id')}")
print(f"first_name: {repr(case.get('first_name'))}")
print(f"last_name: {repr(case.get('last_name'))}")
print(f"has_imf: {repr(case.get('has_imf'))}")

# Import and use the same logic as evaluate_summary
from evaluate_summary import call_assessment_api

print("\n=== Calling API ===")
result = call_assessment_api(case)

if result:
    print("✅ Success!")
    print(f"Keys: {list(result.keys())}")
else:
    print("❌ Failed - check DEBUG output above")
