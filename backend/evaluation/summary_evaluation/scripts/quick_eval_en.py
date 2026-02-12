"""
Quick Evaluation Script for English Version - Edit parameters here and run!
"""
import os
import sys
from pathlib import Path
from tqdm import tqdm

# ============================================
# 🔧 EDIT HERE - CONFIGURATION
# ============================================

# Number of test cases to run
SAMPLE_SIZE = 100  # Change to None to run all

# Show detailed reasoning
VERBOSE = True  # Change to True to see reasoning for each metric

# Output directory
OUTPUT_DIR = "../results/en"

# Test cases file
TEST_FILE = "../generated_test_cases.csv"

# Language setting for evaluation criteria
LANGUAGE = "en"  # Use English evaluation criteria

# ============================================
# Don't edit below this
# ============================================

def main():
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"📂 Working directory: {script_dir}")
    
    # Load API key from .env (backend/.env)
    env_file = Path(__file__).parent.parent.parent.parent / ".env"
    print(f"📂 Looking for .env at: {env_file}")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("DEEPSEEK_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    os.environ["DEEPSEEK_API_KEY"] = api_key
                    print(f"✅ Loaded DEEPSEEK_API_KEY from {env_file}")
                    break
    
    # Check for required API key
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ DEEPSEEK_API_KEY not found!")
        print(f"   Please add it to: {env_file}")
        print(f"   All metrics now use DeepSeek!")
        sys.exit(1)
    
    # Build command arguments
    args = ["--csv", TEST_FILE, "--output", OUTPUT_DIR, "--language", LANGUAGE]
    
    if SAMPLE_SIZE is not None:
        args.extend(["--sample", str(SAMPLE_SIZE)])
    
    if VERBOSE:
        args.append("--verbose")
    
    print("\n" + "="*60)
    print("🚀 Quick Evaluation - English Version")
    print("="*60)
    print(f"📊 Sample Size: {SAMPLE_SIZE if SAMPLE_SIZE else 'All'}")
    print(f"📁 Test File: {TEST_FILE}")
    print(f"💾 Output: {OUTPUT_DIR}")
    print(f"📝 Verbose: {VERBOSE}")
    print(f"🌐 Language: {LANGUAGE}")
    print("="*60 + "\n")
    
    # Import and run
    sys.argv = ["evaluate_summary.py"] + args
    
    # Add parent directory to path for imports
    sys.path.insert(0, str(script_dir.parent))
    
    # Import evaluate_summary module
    import evaluate_summary
    evaluate_summary.main()


if __name__ == "__main__":
    main()
