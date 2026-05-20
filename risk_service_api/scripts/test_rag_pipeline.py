"""
RAG Pipeline Test Suite
─────────────────────────
ทดสอบ RAG pipeline กับชุดคำถามที่ครอบคลุมหลากหลายหัวข้อจากเอกสาร
"""
import sys, os, asyncio, logging, json, time, csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

logging.basicConfig(
    level=logging.WARNING,  # ลด noise log ให้ดูผลลัพธ์ง่าย
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)

from app.services.rag.pipeline import answer_patient_question

# =====================================================================
#  Load Test Cases from CSV
# =====================================================================
def load_test_cases():
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "evaluation", "rag_eval", "test_cases.csv"))
    test_cases = []
    
    if not os.path.exists(csv_path):
        print(f"Test cases CSV not found at: {csv_path}")
        return test_cases
        
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            if row.get("test_case") and row["test_case"].strip():
                # Parse mock contexts
                mock_profile = {}
                if row.get("mock_profile"):
                    try:
                        mock_profile = json.loads(row["mock_profile"])
                    except Exception as e:
                        logging.error(f"Failed to parse mock_profile on row {i}: {e}")
                        
                mock_symptoms = {}
                if row.get("mock_symptoms"):
                    try:
                        mock_symptoms = json.loads(row["mock_symptoms"])
                    except Exception as e:
                        logging.error(f"Failed to parse mock_symptoms on row {i}: {e}")
                
                test_cases.append({
                    "id": i,
                    "question": row["test_case"].strip(),
                    "expected_answer": row.get("golden_response", "").strip(),
                    "mock_profile": mock_profile,
                    "mock_symptoms": mock_symptoms
                })
    return test_cases

TEST_QUESTIONS = load_test_cases()


# =====================================================================
#  Runner
# =====================================================================
async def run_single_test(test_case: dict) -> dict:
    """Run a single test case and return results."""
    q = test_case["question"]
    profile = test_case.get("mock_profile", {})
    symptoms = test_case.get("mock_symptoms", {})
    t0 = time.perf_counter()
    
    # Construct patient context
    patient_context_mock = {
        "patient_profile": profile,
        "current_symptoms": symptoms,
        "risk_assessment": {} # Leave empty to force RAG
    }
    
    result = await answer_patient_question(q, patient_context_mock)
    
    elapsed = time.perf_counter() - t0
    
    is_hybrid = result["source"] == "hybrid"
    
    # Extract locations where chunks were found
    found_locations = []
    for c in result.get("used_chunks", []):
        meta = c.get("metadata", {})
        src = meta.get("source", "Unknown File")
        sec = meta.get("section", "Unknown Section")
        # Line numbers are not kept by proposition chunking, but we have sections
        loc_str = f"File: {src} | Section: {sec}"
        if loc_str not in found_locations: # Remove duplicates
            found_locations.append(loc_str)
            
    found_in_str = "\n".join(found_locations)

    return {
        "id": test_case["id"],
        "question": q,
        "expected_answer": test_case["expected_answer"],
        "mock_profile": profile,
        "mock_symptoms": symptoms,
        "source": result["source"],
        "chunks": len(result["used_chunks"]),
        "found_in": found_in_str,
        "full_answer": result["answer"],
        "time_s": round(elapsed, 1),
        "got_rag": is_hybrid,
    }


def print_results(results: list):
    """Print formatted results table."""
    print("\n" + "=" * 100)
    print("RAG PIPELINE TEST RESULTS")
    print("=" * 100)
    
    total = len(results)
    
    print(f"\n{'ID':>3} | {'Src':<10} | {'Chunks':>6} | {'Time':>5} | Question")
    print("-" * 100)
    
    for r in results:
        print(f"{r['id']:>3} | {r['source']:<10} | {r['chunks']:>6} | {r['time_s']:>4.1f}s | {r['question'][:60]}")
    
    print("-" * 100)
    
    # Print answers
    print("\n" + "=" * 100)
    print("ANSWERS")
    print("=" * 100)
    for r in results:
        print(f"\nQ{r['id']}: {r['question']}")
        print(f"   Source: {r['source']} | Chunks: {r['chunks']} | Time: {r['time_s']}s")
        if r.get("found_in"):
            print(f"   Found in: {r.get('found_in').replace(chr(10), ', ')}")
       
    
    # Setup results directory
    results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "evaluation", "rag_eval", "results"))
    os.makedirs(results_dir, exist_ok=True)

    # Save full results to file
    output_path = os.path.join(results_dir, "rag_test_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nFull results saved to: {output_path}")

    # Save to CSV
    csv_path = os.path.join(results_dir, "rag_test_results.csv")
    
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "question", "source", "chunks", "found_in", "time_s", "got_rag", "answer", "expected_answer", "mock_profile", "mock_symptoms"])
        for r in results:
            writer.writerow([
                r["id"], 
                r["question"], 
                r["source"], 
                r["chunks"], 
                r.get("found_in", ""), 
                r["time_s"], 
                r["got_rag"], 
                r.get("full_answer", ""), 
                r.get("expected_answer", ""),
                json.dumps(r.get("mock_profile", {}), ensure_ascii=False),
                json.dumps(r.get("mock_symptoms", {}), ensure_ascii=False)
            ])
    print(f"CSV results saved to: {csv_path}")


async def main():
    if not TEST_QUESTIONS:
        print("No test questions found. Exiting.")
        return
        
    print(f"Running {len(TEST_QUESTIONS)} test questions from CSV...\n")
    
    results = []
    for i, test in enumerate(TEST_QUESTIONS):
        print(f"[{i+1}/{len(TEST_QUESTIONS)}] Testing Q{test['id']}: {test['question'][:50]}...")
        result = await run_single_test(test)
        results.append(result)
        print(f"  → {result['source']} | {result['chunks']} chunks | {result['time_s']}s")
    
    print_results(results)


if __name__ == "__main__":
    asyncio.run(main())
