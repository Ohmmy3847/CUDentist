"""
Quick Print Summary Script - แก้ parameter ตรงนี้แล้วกดรันเลย!
"""
import json
import sys
from pathlib import Path

# ============================================
# 🔧 แก้ตรงนี้ - CONFIGURATION
# ============================================

# ใช้ไฟล์ล่าสุด หรือระบุไฟล์เฉพาะ
USE_LATEST = False  # True = ใช้ไฟล์ล่าสุด, False = ใช้ SPECIFIC_FILE

# ระบุไฟล์เฉพาะ (ถ้า USE_LATEST = False)
SPECIFIC_FILE = "backend/evaluation/results/evaluation_reasons_20260111_110623.json"

# แสดงเหตุผลแบบเต็ม (multi-line format)
SHOW_FULL = True  # True = แยกหลายบรรทัด, False = บรรทัดเดียว

# แสดงเฉพาะ cases ที่ fail
FAILED_ONLY = False  # True = เฉพาะที่ fail, False = แสดงทั้งหมด

# แสดง case เฉพาะ (ใส่ case_id หรือ None)
SPECIFIC_CASE = None  # เช่น "case_045" หรือ None

# ============================================
# ไม่ต้องแก้ด้านล่างนี้
# ============================================

def print_case_summary(case_data, show_full_reason=False):
    """แสดงสรุปผล 1 case พร้อมคะแนนและเหตุผล"""
    
    case_id = case_data['case_id']
    risk = case_data.get('expected_risk_level', 'N/A')
    avg = case_data['average']
    passed = case_data['passed']
    
    # Header
    print("\n" + "="*80)
    print(f"📋 Case: {case_id} | Risk: {risk} | Overall: {avg:.2f} {'✅' if passed else '❌'}")
    print("="*80)
    
    
    # Metrics with scores and reasons
    metrics = [
        ('faithfulness', 'Faithfulness (QAG)', '🔍'),
        ('conciseness', 'Conciseness (G-Eval)', '📏'),
        ('medical_correctness', 'Medical Correctness (G-Eval)', '⚕️'),
        ('helpfulness', 'Helpfulness (G-Eval)', '💡'),
    ]
    
    for metric_key, metric_name, icon in metrics:
        score = case_data.get(metric_key, 0)
        reason = case_data.get(f"{metric_key}_reason", "")
        status = "✓" if score >= 0.7 else "✗"
        
        print(f"\n{icon} {metric_name}: {score:.2f} {status}")
        
        if reason:
            if show_full_reason:
                print(f"   💬 Reason:")
                lines = reason.split('\n')
                for line in lines:
                    print(f"      {line}")
            else:
                print(f"   💬 {reason}")


def print_summary_stats(results):
    """แสดงสถิติรวม"""
    
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "="*80)
    print("📊 OVERALL STATISTICS")
    print("="*80)
    print(f"Total Cases: {total}")
    print(f"Passed: {passed} ({pass_rate:.1f}%)")
    print(f"Failed: {total - passed} ({100-pass_rate:.1f}%)")
    
    # Average scores per metric
    print("\n📈 Average Scores by Metric:")
    metric_names = ['faithfulness', 'conciseness', 
               'medical_correctness', 'helpfulness']
    
    for metric in metric_names:
        scores = [r[metric] for r in results if metric in r]
        if scores:
            avg = sum(scores) / len(scores)
            status = "✓" if avg >= 0.7 else "✗"
            print(f"  {metric:20s}: {avg:.3f} {status}")
    
    # Overall average
    avg_overall = sum(r['average'] for r in results) / total if total > 0 else 0
    print(f"\n  {'OVERALL':20s}: {avg_overall:.3f} {'✓' if avg_overall >= 0.7 else '✗'}")


def print_failed_cases(results, show_full=False):
    """แสดงเฉพาะ cases ที่ fail พร้อมปัญหา"""
    
    failed = [r for r in results if not r['passed']]
    if not failed:
        print("\n🎉 All cases passed!")
        return
    
    print("\n" + "="*80)
    print(f"❌ FAILED CASES ({len(failed)}/{len(results)})")
    print("="*80)
    
    for case in failed:
        case_id = case['case_id']
        avg = case['average']
        
        metrics = ['faithfulness', 'conciseness', 
                   'medical_correctness', 'helpfulness']
        
        print(f"\n📋 {case_id} (Avg: {avg:.2f})")
        
        for metric in metrics:
            score = case.get(metric, 0)
            if score < 0.7:
                reason = case.get(f"{metric}_reason", "")
                
                if show_full:
                    print(f"   ❌ {metric}: {score:.2f}")
                    if reason:
                        lines = reason.split('\n')
                        for line in lines:
                            print(f"      {line}")
                else:
                    print(f"   ❌ {metric}: {score:.2f} - {reason}")


def main():
    print("\n" + "="*60)
    print("📊 Quick Print Summary")
    print("="*60)
    print(f"📁 Use Latest: {USE_LATEST}")
    print(f"📝 Show Full: {SHOW_FULL}")
    print(f"❌ Failed Only: {FAILED_ONLY}")
    print(f"🎯 Specific Case: {SPECIFIC_CASE if SPECIFIC_CASE else 'All'}")
    print("="*60 + "\n")
    
    # Find results file
    if USE_LATEST:
        results_dir = Path("results")
        reason_files = sorted(results_dir.glob("evaluation_reasons_*.json"), reverse=True)
        if not reason_files:
            print("❌ No evaluation results found")
            sys.exit(1)
        results_file = reason_files[0]
    else:
        results_file = Path(SPECIFIC_FILE)
        if not results_file.exists():
            print(f"❌ File not found: {SPECIFIC_FILE}")
            sys.exit(1)
    
    # Load results
    print(f"📂 Loading: {results_file}")
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print(f"✅ Loaded {len(results)} cases\n")
    
    # Print based on mode
    if SPECIFIC_CASE:
        # Show specific case
        case = next((r for r in results if r['case_id'] == SPECIFIC_CASE), None)
        if case:
            print("AI Answer:\n" )
            print(case['api_response']['summary'])
            print_case_summary(case, show_full_reason=SHOW_FULL)
        else:
            print(f"❌ Case {SPECIFIC_CASE} not found")
    
    elif FAILED_ONLY:
 
       
        # Show only failed cases
        print_summary_stats(results)
        print_failed_cases(results, show_full=SHOW_FULL)
        
    
    else:
        # Show all cases
    
        print_summary_stats(results)
        for case in results:
            print("AI Answer:\n" )
            print(case['api_response']['summary']['summary'])
            print_case_summary(case, show_full_reason=SHOW_FULL)
    
        print_failed_cases(results, show_full=SHOW_FULL)
    
    print("\n" + "="*80)
    print("✨ Summary complete!")


if __name__ == "__main__":
    main()
