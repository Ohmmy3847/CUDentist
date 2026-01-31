"""
Print Evaluation Summary with Scores and Reasons
แสดงสรุปผลการประเมินพร้อมคะแนนและเหตุผล
"""
import json
import sys
import argparse
from pathlib import Path


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
        ('answer_relevancy', 'Answer Relevancy (RAG)', '🎯'),
        ('medical_correctness', 'Medical Correctness (G-Eval)', '⚕️'),
        ('contextual_relevancy', 'Contextual Relevancy', '📝'),
        ('helpfulness', 'Helpfulness (G-Eval)', '💡'),
    ]
    
    for metric_key, metric_name, icon in metrics:
        score = case_data.get(metric_key, 0)
        reason = case_data.get(f"{metric_key}_reason", "")
        status = "✓" if score >= 0.7 else "✗"
        
        print(f"\n{icon} {metric_name}: {score:.2f} {status}")
        
        if reason:
            # Show full reason always (no truncation unless --full for multi-line format)
            if show_full_reason:
                # Full reason with proper multi-line formatting
                print(f"   💬 Reason:")
                lines = reason.split('\n')
                for line in lines:  # Show all lines
                    print(f"      {line}")
            else:
                # Show full reason in single format (no truncation)
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
        
        # Find metrics that failed
        failed_metrics = []
        metrics = ['faithfulness', 'conciseness', 'answer_relevancy', 
                   'medical_correctness', 'contextual_relevancy', 'helpfulness']
        
        print(f"\n📋 {case_id} (Avg: {avg:.2f})")
        
        for metric in metrics:
            score = case.get(metric, 0)
            if score < 0.7:
                reason = case.get(f"{metric}_reason", "")
                
                # Format reason based on mode
                if show_full:
                    # Full reason with proper formatting
                    print(f"   ❌ {metric}: {score:.2f}")
                    if reason:
                        # Indent multi-line reasons
                        lines = reason.split('\n')
                        for line in lines:  # Show all lines
                            print(f"      {line}")
                else:
                    # Show full reason (no truncation)
                    print(f"   ❌ {metric}: {score:.2f} - {reason}")


def main():
    parser = argparse.ArgumentParser(description="Print Evaluation Summary")
    parser.add_argument("--file", "-f", help="Path to evaluation_reasons JSON file")
    parser.add_argument("--latest", "-l", action="store_true", help="Use latest results file")
    parser.add_argument("--full", action="store_true", help="Show full reasons (not truncated)")
    parser.add_argument("--failed-only", action="store_true", help="Show only failed cases")
    parser.add_argument("--case", help="Show specific case ID")
    args = parser.parse_args()
    
    # Find results file
    if args.file:
        results_file = Path(args.file)
    elif args.latest:
        results_dir = Path("results")
        reason_files = sorted(results_dir.glob("evaluation_reasons_*.json"), reverse=True)
        if not reason_files:
            print("❌ No evaluation results found")
            sys.exit(1)
        results_file = reason_files[0]
    else:
        print("❌ Please specify --file or --latest")
        sys.exit(1)
    
    # Load results
    print(f"📂 Loading: {results_file}")
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print(f"✅ Loaded {len(results)} cases")
    
    # Print based on mode
    if args.case:
        # Show specific case
        case = next((r for r in results if r['case_id'] == args.case), None)
        if case:
            print_case_summary(case, show_full_reason=args.full)
        else:
            print(f"❌ Case {args.case} not found")
    
    elif args.failed_only:
        # Show only failed cases
        print_failed_cases(results, show_full=args.full)
        print_summary_stats(results)
    
    else:
        # Show all cases
        for case in results:
            print_case_summary(case, show_full_reason=args.full)
        
        print_summary_stats(results)
        print_failed_cases(results, show_full=args.full)
    
    print("\n" + "="*80)
    print("✨ Summary complete!")


if __name__ == "__main__":
    main()
