"""
Quick Evaluation Script - แก้ parameter ตรงนี้แล้วกดรันเลย!
"""
import os
import sys
from pathlib import Path
from tqdm import tqdm
# ============================================
# 🔧 แก้ตรงนี้ - CONFIGURATION
# ============================================

# จำนวน test cases ที่จะรัน
SAMPLE_SIZE = 100  # เปลี่ยนเป็น None ถ้าต้องการรันทั้งหมด

# แสดงรายละเอียดเหตุผล
VERBOSE = True  # เปลี่ยนเป็น True ถ้าต้องการเห็นเหตุผลแต่ละ metric

# Output directory
OUTPUT_DIR = "results"

# Test cases file
TEST_FILE = "generated_test_cases.csv"

# ============================================
# ไม่ต้องแก้ด้านล่างนี้
# ============================================

def main():
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"📂 Working directory: {script_dir}")
    
    # Load API key from .env (backend/.env)
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("GOOGLE_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    os.environ["GOOGLE_API_KEY"] = api_key
                    print(f"✅ Loaded GOOGLE_API_KEY from {env_file}")
                    break
    
    # Check for required API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not found!")
        print(f"   Please add it to: {env_file}")
        print(f"   All metrics now use Gemini (no OpenAI key needed!)")
        sys.exit(1)
    
    # Build command arguments
    args = ["--csv", TEST_FILE, "--output", OUTPUT_DIR]
    
    if SAMPLE_SIZE is not None:
        args.extend(["--sample", str(SAMPLE_SIZE)])
    
    if VERBOSE:
        args.append("--verbose")
    
    print("\n" + "="*60)
    print("🚀 Quick Evaluation")
    print("="*60)
    print(f"📊 Sample Size: {SAMPLE_SIZE if SAMPLE_SIZE else 'All'}")
    print(f"📁 Test File: {TEST_FILE}")
    print(f"💾 Output: {OUTPUT_DIR}")
    print(f"📝 Verbose: {VERBOSE}")
    print("="*60 + "\n")
    
    # Import and run
    sys.argv = ["evaluate_summary.py"] + args
    
    # Import evaluate_summary module
    import evaluate_summary
    evaluate_summary.main()


if __name__ == "__main__":
    main()
