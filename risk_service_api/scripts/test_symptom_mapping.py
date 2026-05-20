"""
Quick test: symptom mapping pipeline for 1 case.

Usage:
    python risk_service_api/scripts/test_symptom_mapping.py
    python risk_service_api/scripts/test_symptom_mapping.py "ปากแตกๆ แห้งมาก"
"""
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.WARNING)

from app.services.symptom.mapping import map_symptom, get_collection

INPUT = sys.argv[1] if len(sys.argv) > 1 else "ปากแตกๆ แห้งมาก"


def main():
    print(f"\nPipeline: Top-5 + Strict LLM Classify")
    print(f"\nInput: \"{INPUT}\"")

    collection = get_collection()
    result = map_symptom(INPUT, collection)

    print(f"\nResult:")
    print(f"  matched       : {result.matched}")
    print(f"  symptom       : {result.matched_symptom or '—'}")
    print(f"  similarity    : {result.similarity:.4f}")
    print(f"  tier          : {result.tier}")
    if result.reason:
        print(f"  reason        : {result.reason}")
    if result.risk_level:
        print(f"  risk_level    : {result.risk_level}")
    if result.recommendation:
        print(f"  recommendation: {result.recommendation}")


if __name__ == "__main__":
    main()
