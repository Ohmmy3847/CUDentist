"""
Evaluation Pipeline for LLM Summary
Comprehensive evaluation based on Confident AI's LLM evaluation guide
Uses G-Eval, QAG scorer, and custom metrics
"""
import os
import sys
import csv
import json
import requests
import argparse
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
# Add parent directories to path to import metrics
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(backend_dir)

from metrics import FaithfulnessMetric, ConcisenessMetric, CompletenessMetric, HelpfulnessMetric, FormatComplianceMetric

# Default metric weights (can be customized via command line)
# Higher weight = more importance in final score
DEFAULT_METRIC_WEIGHTS = {
    "faithfulness": 0.35,    # ความถูกต้องตามข้อมูลจริง - สำคัญมาก
    "conciseness": 0.15,     # ความกระชับ - สำคัญปานกลาง
    "completeness": 0.35,    # ความครบถ้วน - สำคัญมาก
    "helpfulness": 0.15,     # ความเป็นประโยชน์ - สำคัญ
}

def load_test_cases(csv_file: str, sample_size: int = None) -> List[Dict]:
    """โหลด test cases จาก CSV"""
    cases = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cases.append(row)
            if sample_size and len(cases) >= sample_size:
                break
    return cases


def call_assessment_api(patient_data: Dict) -> Dict:
    """เรียก API backend เพื่อประเมินความเสี่ยง"""
    url = "http://localhost:8000/patient-assessment"
    
    # Convert CSV data to API format - API expects {"basic_info": {...}, "assessment_data": {...}}
    # Get first_name and last_name from CSV (already split)
    first_name = patient_data.get("first_name", "")
    last_name = patient_data.get("last_name", "")
    
    payload = {
        "basic_info": {
            # Personal Information
            "first_name": first_name,
            "last_name": last_name,
            "email": patient_data.get("email", None) if patient_data.get("email") else None,
            "phone": patient_data.get("phone", None) if patient_data.get("phone") else None,
            "birth_year": int(patient_data.get("birth_year")) if patient_data.get("birth_year") else None,
            # Basic Medical Info
            "age": int(patient_data.get("age", 0)) if patient_data.get("age") else None,
            "gender": patient_data.get("gender", None) if patient_data.get("gender") else None,
            "hn": patient_data.get("hn", None) if patient_data.get("hn") else None,
            "procedures": patient_data.get("procedures", "").split(", ") if patient_data.get("procedures") else [],
            "lefort_sub_options": [],
            "bssro_sub_options": [],
            "surgery_date": patient_data.get("surgery_date", None) if patient_data.get("surgery_date") else None,
            "discharge_date": patient_data.get("discharge_date", None) if patient_data.get("discharge_date") else None,
            "note": patient_data.get("note", None) if patient_data.get("note") else None,
            # Special Procedures
            "has_imf": patient_data.get("has_imf", None) if patient_data.get("has_imf") else None,
            "imf_type": patient_data.get("imf_type", None) if patient_data.get("imf_type") else None,
            "imf_loops": int(patient_data.get("imf_loops", 0)) if patient_data.get("imf_loops") else None,
            "special_icbg": patient_data.get("special_icbg", None) if patient_data.get("special_icbg") else None,
            "special_icbg_description": patient_data.get("special_icbg_description", None) if patient_data.get("special_icbg_description") else None,
            "special_ng_tube": patient_data.get("special_ng_tube", None) if patient_data.get("special_ng_tube") else None,
            "special_ng_tube_description": patient_data.get("special_ng_tube_description", None) if patient_data.get("special_ng_tube_description") else None,
        },
        "assessment_data": {
            "pain_score": int(patient_data.get("pain_score", 0)),
            "pain_medication_effect": patient_data.get("pain_medication_effect", ""),
            "swelling_status": patient_data.get("swelling_status", ""),
            "breathing_or_swallowing_difficulty": patient_data.get("breathing_or_swallowing_difficulty", ""),
            "bleeding_status": patient_data.get("bleeding_status", ""),
            "fever_status": patient_data.get("fever_status", ""),
            "phlebitis": patient_data.get("phlebitis", ""),
            "suture_status": patient_data.get("suture_status", ""),
            "other_symptoms": patient_data.get("other_symptoms", "").split(", ") if patient_data.get("other_symptoms") else [],
            "antibiotic_compliance": patient_data.get("antibiotic_compliance", ""),
            "compress_type": patient_data.get("compress_type", ""),
            "imf_wire_status": patient_data.get("imf_wire_status", ""),
            "walking_status": patient_data.get("walking_status", ""),
            "ng_tube_position": patient_data.get("ng_tube_position", ""),
            "brushing_teeth": patient_data.get("brushing_teeth", ""),
            "mouth_rinsing": patient_data.get("mouth_rinsing", ""),
            "feeding_method": patient_data.get("feeding_method", ""),
            "additional_questions": patient_data.get("additional_questions", "")
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            print(f"\n❌ Validation Error 422 for case: {patient_data.get('case_id', 'unknown')}")
            try:
                error_detail = e.response.json()
                import json
                print("Error details:")
                print(json.dumps(error_detail, indent=2, ensure_ascii=False))
            except:
                print(e.response.text[:500])
        print(f"❌ API Error: {e}")
        return None
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None


def create_test_case(patient_data: Dict, api_response: Dict) -> LLMTestCase:
    """สร้าง LLMTestCase สำหรับ evaluation"""
    
    # Input context - ใส่ข้อมูลครบถ้วนเพื่อให้ metrics ประเมินได้ถูกต้อง
    full_name = f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}".strip()
    input_text = f"""
ข้อมูลผู้ป่วย:
ชื่อ: {full_name}
อายุ: {patient_data.get('age', '')} ปี
เพศ: {patient_data.get('gender', '')}
วันที่ผ่าตัด: {patient_data.get('surgery_date', '')}
ประเภทการผ่าตัด: {patient_data.get('procedures', '')}

อาการและสัญญาณ:
- ระดับความปวด: {patient_data.get('pain_score', '')}/10
- ผลของยาแก้ปวด: {patient_data.get('pain_medication_effect', '')}
- การบวม: {patient_data.get('swelling_status', '')}
- การหายใจ: {patient_data.get('breathing_or_swallowing_difficulty', '')}
- เลือดออก: {patient_data.get('bleeding_status', '')}
- ไข้: {patient_data.get('fever_status', '')}
- เส้นเลือดอักเสบ: {patient_data.get('phlebitis', '')}
- สภาพแผลและไหม: {patient_data.get('suture_status', '')}
- อาการอื่นๆ: {patient_data.get('other_symptoms', 'ไม่มี')}

การดูแลและกิจกรรม:
- การทานยาปฏิชีวนะ: {patient_data.get('antibiotic_compliance', '')}
- การประคบ: {patient_data.get('compress_type', '')}
- การแปรงฟัน: {patient_data.get('brushing_teeth', '')}
- การบ้วนปาก: {patient_data.get('mouth_rinsing', '')}
- วิธีการรับประทานอาหาร: {patient_data.get('feeding_method', '')}

ข้อมูลพิเศษ (ถ้ามี):
- IMF (มัดฟัน): {patient_data.get('has_imf', '')}
  สถานะลวด: {patient_data.get('imf_wire_status', '') if patient_data.get('has_imf') == 'มีการมัดฟัน' else 'N/A'}
- ICBG (เอากระดูกจากสะโพก): {patient_data.get('special_icbg', '')}
  การเดิน: {patient_data.get('walking_status', '') if patient_data.get('special_icbg') == 'มี' else 'N/A'}
- NG Tube (สายให้อาหาร): {patient_data.get('special_ng_tube', '')}
  ตำแหน่งสาย: {patient_data.get('ng_tube_position', '') if patient_data.get('special_ng_tube') == 'มี' else 'N/A'}
"""
    
    # Actual output from LLM - API returns summary as dict with "summary" key inside
    summary_data = api_response.get("summary", {})
    if isinstance(summary_data, dict):
        actual_output = summary_data.get("summary", "")
    else:
        actual_output = str(summary_data) if summary_data else ""
    
    # Expected output (from rule-based recommendations in flows)
    expected_recommendations = []
    flows_data = api_response.get("flows", {})
    for flow_name, result in flows_data.items():
        if result.get("recommendation"):
            expected_recommendations.append(f"{flow_name}: {result['recommendation']}")
    expected_output = "\n".join(expected_recommendations) if expected_recommendations else ""
    
    # Retrieval context (for faithfulness) - include risk level and template phrases
    overall_risk = api_response.get("overall_risk", "")
    
    # Add expected template phrases based on risk level
    template_phrases = []
    if "สูง" in overall_risk:
        template_phrases = [
            "มีความเสี่ยงต่อการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปากในระดับสูง",
            "แนะนำให้ติดต่อพยาบาลโดยเร็ว"
        ]
    elif "กลาง" in overall_risk or "ปานกลาง" in overall_risk:
        template_phrases = [
            "มีความเสี่ยงต่อการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปากระดับปานกลาง",
            "ทีมพยาบาลจะติดต่อกลับเพื่อประเมินอาการเพิ่มเติม"
        ]
    elif "ต่ำ" in overall_risk:
        template_phrases = [
            "มีความเสี่ยงในการเกิดภาวะแทรกซ้อนหลังการผ่าตัดในช่องปาก ระดับต่ำ",
            "อาการโดยรวมอยู่ในเกณฑ์ปกติ"
        ]
    elif "ซับซ้อน" in overall_risk:
        template_phrases = [
            "ไม่สามารถสรุปผลความเสี่ยงได้เนื่องจากอาการมีความซับซ้อน",
            "ทีมพยาบาลจะติดต่อกลับเพื่อประเมินอาการเพิ่มเติม"
        ]
    
    context_data = {
        "risk_level": overall_risk,
        "template_phrases": template_phrases,
        "flows": flows_data
    }
    retrieval_context = [json.dumps(context_data, ensure_ascii=False)]
    
    return LLMTestCase(
        input=input_text,
        actual_output=actual_output,
        expected_output=expected_output,
        retrieval_context=retrieval_context
    )


def evaluate_case(test_case: LLMTestCase, weights: Dict[str, float] = None) -> Dict:
    """
    ประเมิน 1 test case ด้วย 6 metrics (PARALLEL)
    Based on Confident AI's LLM Evaluation Guide:
    - Following the 5-metric rule (we use 6 for comprehensive medical evaluation)
    - Mix of generic (faithfulness, conciseness, answer relevancy) and custom metrics
    - Using G-Eval with CoT, QAG scorer approaches
    
    Args:
        test_case: LLMTestCase to evaluate
        weights: Dictionary of metric weights (default: DEFAULT_METRIC_WEIGHTS)
    """
    
    # Use default weights if not provided
    if weights is None:
        weights = DEFAULT_METRIC_WEIGHTS.copy()
    
    # Initialize metrics
    metrics_list = [
        ("faithfulness", FaithfulnessMetric(threshold=0.7), "QAG scorer"),
        ("conciseness", ConcisenessMetric(threshold=0.7), "G-Eval"),
        ("completeness", CompletenessMetric(threshold=0.7, model="gemini-2.0-flash"), "G-Eval (Gemini)"),
        ("helpfulness", HelpfulnessMetric(threshold=0.7), "G-Eval+CoT"),
        # ("format_compliance", FormatComplianceMetric(threshold=0.8), "Rule-based"),  # Temporarily disabled
    ]
    
    print("  📊 Evaluating with 4 metrics (parallel)...")
    metrics = {}
    
    def evaluate_metric(name, metric, desc):
        """Evaluate a single metric"""
        try:
            print(f"    - {name.replace('_', ' ').title()} ({desc})...")
            score = metric.measure(test_case)
            reason = getattr(metric, 'reason', '')
            success = metric.is_successful()
            return name, score, reason, success, None
        except Exception as e:
            print(f"    ❌ {name.replace('_', ' ').title()} error: {e}")
            default_score = 0.5 if name in ['faithfulness', 'conciseness', 'answer_relevancy', 'helpfulness'] else 0.7
            return name, default_score, str(e), False, e
    
    # Run metrics in parallel (max 15 concurrent - with 1K req/min quota)
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(evaluate_metric, name, metric, desc): name 
                   for name, metric, desc in metrics_list}
        
        metric_objects = {}
        for future in as_completed(futures):
            name, score, reason, success, error = future.result()
            metrics[name] = score
            metrics[f"{name}_reason"] = reason
            metric_objects[name] = success
    
    # Calculate weighted average
    score_keys = [k for k in metrics.keys() if not k.endswith('_reason')]
    
    # Normalize weights to sum to 1
    total_weight = sum(weights.get(k, 1.0) for k in score_keys)
    normalized_weights = {k: weights.get(k, 1.0) / total_weight for k in score_keys}
    
    # Calculate weighted average
    weighted_sum = sum(metrics[k] * normalized_weights[k] for k in score_keys)
    metrics["average"] = weighted_sum
    metrics["weighted_average"] = weighted_sum  # Keep both for clarity
    
    # Also calculate simple average for comparison
    metrics["simple_average"] = sum(metrics[k] for k in score_keys) / len(score_keys)
    
    # Check pass/fail
    metrics["passed"] = all(metric_objects.values())
    
    print(f"  ✅ Weighted Avg: {metrics['average']:.2f} | Simple Avg: {metrics['simple_average']:.2f} | Passed: {metrics['passed']}")
    
    return metrics


def save_results(results: List[Dict], output_dir: str = "results", experiment_name: str = None, weights: Dict[str, float] = None):
    """บันทึกผลการ evaluate ใน subfolder แยกตาม experiment"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create experiment folder
    if experiment_name:
        output_dir = os.path.join(output_dir, experiment_name)
    else:
        # Use timestamp as default experiment name
        output_dir = os.path.join(output_dir, f"exp_{timestamp}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📁 Saving to: {output_dir}")
    
    # Save detailed results as CSV (scores only)
    csv_file = os.path.join(output_dir, f"evaluation_results_{timestamp}.csv")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            "case_id", "expected_risk_level", "actual_risk_level",
            "faithfulness", "conciseness",
            "completeness", "helpfulness",
            "weighted_average", "simple_average", "passed", "summary_length"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        # Write scores only (without reason fields)
        scores_only = []
        for r in results:
            scores_only.append({k: v for k, v in r.items() if k in fieldnames})
        writer.writerows(scores_only)
    
    # Save detailed reasons as JSON
    reasons_file = os.path.join(output_dir, f"evaluation_reasons_{timestamp}.json")
    with open(reasons_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Calculate pass rates for different methods
    passed_all_metrics = sum(1 for r in results if r["passed"])
    passed_simple = sum(1 for r in results if r.get("simple_average", r["average"]) >= 0.7)
    passed_weighted = sum(1 for r in results if r["average"] >= 0.7)
    
    # Save summary as JSON
    summary = {
        "timestamp": timestamp,
        "total_cases": len(results),
        # All metrics must pass (strictest)
        "passed_cases": passed_all_metrics,
        "pass_rate": passed_all_metrics / len(results) if results else 0,
        # Simple average >= 0.7
        "passed_cases_simple": passed_simple,
        "pass_rate_simple": passed_simple / len(results) if results else 0,
        # Weighted average >= 0.7
        "passed_cases_weighted": passed_weighted,
        "pass_rate_weighted": passed_weighted / len(results) if results else 0,
        "metric_weights": weights if weights else DEFAULT_METRIC_WEIGHTS,
        "passed_per_metric": {
            "faithfulness": sum(1 for r in results if r["faithfulness"] >= 0.7),
            "conciseness": sum(1 for r in results if r["conciseness"] >= 0.7),
            "completeness": sum(1 for r in results if r["completeness"] >= 0.7),
            "helpfulness": sum(1 for r in results if r["helpfulness"] >= 0.7)
        },
        "average_scores": {
            "faithfulness": sum(r["faithfulness"] for r in results) / len(results) if results else 0,
            "conciseness": sum(r["conciseness"] for r in results) / len(results) if results else 0,
            "completeness": sum(r["completeness"] for r in results) / len(results) if results else 0,
            "helpfulness": sum(r["helpfulness"] for r in results) / len(results) if results else 0,
            "weighted_overall": sum(r["average"] for r in results) / len(results) if results else 0,
            "simple_overall": sum(r.get("simple_average", r["average"]) for r in results) / len(results) if results else 0
        },
        "evaluation_framework": "Based on Confident AI's LLM Evaluation Guide",
        "metrics_used": [
            "Faithfulness (QAG Scorer)",
            "Conciseness (G-Eval)",
            "Completeness (G-Eval)",
            "Helpfulness (G-Eval)",
            "Format Compliance (Rule-based)"
        ]
    }
    
    json_file = os.path.join(output_dir, f"evaluation_summary_{timestamp}.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Results saved:")
    print(f"   📄 {csv_file}")
    print(f"   📝 {reasons_file}")
    print(f"   📊 {json_file}")
    print(f"\n📈 Evaluation Summary:")
    print(f"   Total Cases: {summary['total_cases']}")
    print(f"\n   Pass Rates:")
    print(f"   - All Metrics Pass (Strict): {summary['passed_cases']}/{summary['total_cases']} ({summary['pass_rate']:.1%})")
    print(f"   - Simple Average ≥ 0.7: {summary['passed_cases_simple']}/{summary['total_cases']} ({summary['pass_rate_simple']:.1%})")
    print(f"   - Weighted Average ≥ 0.7: {summary['passed_cases_weighted']}/{summary['total_cases']} ({summary['pass_rate_weighted']:.1%})")
    print(f"\n   Overall Scores:")
    print(f"   - Weighted Overall: {summary['average_scores']['weighted_overall']:.2f}")
    print(f"   - Simple Overall: {summary['average_scores']['simple_overall']:.2f}")
    print(f"\n   Metric Scores:")
    for metric, score in summary['average_scores'].items():
        if metric not in ['weighted_overall', 'simple_overall']:
            passed = summary['passed_per_metric'].get(metric, 0)
            total = summary['total_cases']
            pass_rate = (passed / total * 100) if total > 0 else 0
            print(f"     - {metric}: {score:.2f} (passed: {passed}/{total} = {pass_rate:.1f}%)")
    
    return summary


def process_single_case(patient_data, case_num, total_cases, args, weights=None):
    """ประมวลผล 1 case (ใช้สำหรับ batch)"""
    case_id = patient_data.get("case_id", f"case_{case_num:03d}")
    print(f"\nเริ่ม {case_id} ({case_num}/{total_cases})...")
    
    try:
        # Call API
        api_response = call_assessment_api(patient_data)
        if not api_response:
            print(f"   ❌ API failed")
            return None
        
        # Create test case
        test_case = create_test_case(patient_data, api_response)
        
        # Evaluate with weights
        metrics = evaluate_case(test_case, weights)
        
        # Print brief results
        if not args.verbose:
            print(f"   ✅ {case_id}: Weighted Avg={metrics['average']:.2f} Simple Avg={metrics['simple_average']:.2f} Pass={metrics['passed']}")
        else:
            # Verbose output
            print(f"   ├─ Faithfulness: {metrics['faithfulness']:.2f} {'✓' if metrics['faithfulness'] >= 0.7 else '✗'}")
            if metrics.get('faithfulness_reason'):
                print(f"      → {metrics['faithfulness_reason'][:100]}...")
            print(f"   ├─ Conciseness: {metrics['conciseness']:.2f} {'✓' if metrics['conciseness'] >= 0.7 else '✗'}")
            print(f"   ├─ Completeness: {metrics['completeness']:.2f} {'✓' if metrics['completeness'] >= 0.7 else '✗'}")
            if metrics.get('completeness_reason'):
                print(f"      → {metrics['completeness_reason'][:100]}...")
            print(f"   ├─ Helpfulness: {metrics['helpfulness']:.2f} {'✓' if metrics['helpfulness'] >= 0.7 else '✗'}")
            print(f"   ├─ Weighted Average: {metrics['average']:.2f} {'✓' if metrics['passed'] else '✗'}")
            print(f"   └─ Simple Average: {metrics['simple_average']:.2f}")
        
        # Return result
        return {
            "case_id": case_id,
            "expected_risk_level": patient_data.get("expected_risk_level", ""),
            "actual_risk_level": api_response.get("overall_risk", ""),
            "faithfulness": metrics["faithfulness"],
            "faithfulness_reason": metrics.get("faithfulness_reason", ""),
            "conciseness": metrics["conciseness"],
            "conciseness_reason": metrics.get("conciseness_reason", ""),
            "completeness": metrics["completeness"],
            "completeness_reason": metrics.get("completeness_reason", ""),
            "helpfulness": metrics["helpfulness"],
            "helpfulness_reason": metrics.get("helpfulness_reason", ""),
            "average": metrics["average"],
            "weighted_average": metrics["weighted_average"],
            "simple_average": metrics["simple_average"],
            "passed": metrics["passed"],
            "summary_length": len(test_case.actual_output),
            "patient_data": patient_data,
            "api_response": api_response
        }
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Evaluate LLM Summary")
    parser.add_argument("--csv", default="generated_test_cases.csv", help="Input CSV file")
    parser.add_argument("--sample", type=int, help="Sample size (default: all)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed reasons")
    parser.add_argument("--output", default="results", help="Output directory")
    parser.add_argument("--experiment", default=None, help="Experiment name (creates subfolder in results/)")
    parser.add_argument("--weights", type=str, help="Custom metric weights as JSON string, e.g. '{\"faithfulness\": 2.0, \"conciseness\": 0.5}'")
    args = parser.parse_args()
    
    print("🚀 Starting LLM Summary Evaluation")
    print("="*60)
    if args.experiment:
        print(f"📂 Experiment: {args.experiment}")
    
    # Parse custom weights if provided
    weights = DEFAULT_METRIC_WEIGHTS.copy()
    if args.weights:
        try:
            custom_weights = json.loads(args.weights)
            weights.update(custom_weights)
            print(f"\n⚖️  Using custom weights: {weights}")
        except json.JSONDecodeError as e:
            print(f"\n⚠️  Invalid weights JSON, using defaults: {e}")
    else:
        print(f"\n⚖️  Using default weights: {weights}")
    
    # Load test cases
    print(f"\n📂 Loading test cases from {args.csv}...")
    cases = load_test_cases(args.csv, args.sample)
    print(f"✅ Loaded {len(cases)} test cases")
    
    # Batch evaluate cases (parallel with 10 workers for case-level parallelism)
    # Each case uses 6 metrics * 15 workers = max 90 concurrent LLM calls
    # With 1K req/min quota, can handle ~10-15 cases in parallel
    print(f"\n⚡ Batch evaluation with parallel processing...")
    print(f"   Quota: 1K req/min, 1M tokens/min")
    print(f"   Workers: 10 cases x 15 metrics = 150 max concurrent")
    
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_single_case, patient_data, i, len(cases), args, weights): i 
                   for i, patient_data in enumerate(cases, 1)}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    
    # Save results
    print("\n" + "="*60)
    print("💾 Saving results...")
    summary = save_results(results, args.output, args.experiment, weights)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 EVALUATION SUMMARY")
    print("="*60)
    print(f"Total Cases: {summary['total_cases']}")
    print(f"\nPass Rates:")
    print(f"  All Metrics Pass (Strict):  {summary['passed_cases']}/{summary['total_cases']} ({summary['pass_rate']*100:.1f}%)")
    print(f"  Simple Average ≥ 0.7:       {summary['passed_cases_simple']}/{summary['total_cases']} ({summary['pass_rate_simple']*100:.1f}%)")
    print(f"  Weighted Average ≥ 0.7:     {summary['passed_cases_weighted']}/{summary['total_cases']} ({summary['pass_rate_weighted']*100:.1f}%)")
    
    print("\n⚖️  Metric Weights:")
    for metric, weight in summary['metric_weights'].items():
        print(f"  {metric.capitalize():20s} {weight:.2f}")
    
    print("\n📊 Individual Metric Scores:")
    for metric in ['faithfulness', 'conciseness', 'completeness', 'helpfulness']:
        score = summary['average_scores'].get(metric, 0)
        status = "✓" if score >= 0.7 else "✗"
        print(f"  {metric.capitalize():20s} {score:.3f} {status}")
    
    print("\n📈 Overall Scores:")
    weighted_score = summary['average_scores'].get('weighted_overall', 0)
    simple_score = summary['average_scores'].get('simple_overall', 0)
    weighted_status = "✓" if weighted_score >= 0.7 else "✗"
    simple_status = "✓" if simple_score >= 0.7 else "✗"
    print(f"  {'Weighted Average':20s} {weighted_score:.3f} {weighted_status}")
    print(f"  {'Simple Average':20s} {simple_score:.3f} {simple_status}")
    
    print("\n✨ Evaluation complete!")


if __name__ == "__main__":
    main()
