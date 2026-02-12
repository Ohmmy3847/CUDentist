#!/usr/bin/env python3
"""
Quick launcher for summary evaluation scripts
Run from backend/evaluation/ directory
"""
import sys
import subprocess
from pathlib import Path

def show_menu():
    print("\n" + "="*60)
    print("📊 Summary Evaluation Launcher")
    print("="*60)
    print("\n🇹🇭 Thai Evaluation:")
    print("  1. Run Thai evaluation (quick_eval_th.py)")
    print("  2. View Thai results (quick_print_th.py)")
    print("\n🇬🇧 English Evaluation:")
    print("  3. Run English evaluation (quick_eval_en.py)")
    print("  4. View English results (quick_print_en.py)")
    print("\n🔧 Other:")
    print("  5. Generate test data")
    print("  6. Test API call")
    print("  7. Exit")
    print("="*60)

def run_script(script_name):
    script_path = Path("summary_evaluation/scripts") / script_name
    if not script_path.exists():
        # Try alternative paths
        if script_name in ["generate_test_data.py"]:
            script_path = Path("summary_evaluation") / script_name
    
    if script_path.exists():
        print(f"\n🚀 Running {script_name}...")
        subprocess.run([sys.executable, str(script_path)])
    else:
        print(f"❌ Script not found: {script_path}")

def main():
    while True:
        show_menu()
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            run_script("quick_eval_th.py")
        elif choice == "2":
            run_script("quick_print_th.py")
        elif choice == "3":
            run_script("quick_eval_en.py")
        elif choice == "4":
            run_script("quick_print_en.py")
        elif choice == "5":
            run_script("generate_test_data.py")
        elif choice == "6":
            run_script("test_api_call.py")
        elif choice == "7":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\n Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
