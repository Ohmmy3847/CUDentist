"""
Quick Print Script for English Evaluation Results
Displays the latest evaluation results for English version
"""
import os
import sys
from pathlib import Path

# Change to script directory
script_dir = Path(__file__).parent
os.chdir(script_dir)

# Import the main print module
sys.path.append(str(script_dir))
import print_eval_summary

# Use English results directory
print_eval_summary.RESULTS_DIR = "../results/en"

if __name__ == "__main__":
    print_eval_summary.main()
