# Evaluation Framework

Comprehensive evaluation system for LLM-generated medical summaries and recommendations.

## 📁 Directory Structure

```
evaluation/
├── EVALUATION_GUIDE.md         # Evaluation methodology guide
├── launcher.py                  # Quick launcher for all scripts 🆕
├── quick_print.py              # Legacy results printer
│
├── criteria/                   # 🆕 Evaluation criteria (LLM prompts)
│   ├── README.md              # Criteria documentation
│   ├── th/                    # Thai criteria files
│   │   ├── conciseness.txt
│   │   ├── completeness.txt
│   │   └── helpfulness.txt
│   └── en/                    # English criteria files
│       ├── conciseness.txt
│       ├── completeness.txt
│       └── helpfulness.txt
│
├── metrics/                    # Metric implementations
│   ├── __init__.py
│   ├── faithfulness.py        # QAG-based faithfulness
│   ├── conciseness.py         # G-Eval conciseness
│   ├── completeness.py        # G-Eval completeness
│   ├── helpfulness.py         # G-Eval helpfulness
│   └── llm_cache.py          # LLM response caching
│
├── summary_evaluation/         # Main evaluation pipeline
│   ├── README.md              # Detailed usage guide
│   ├── evaluate_summary.py   # Core evaluation engine
│   ├── generate_test_data.py # Test case generator
│   ├── generated_test_cases.csv
│   ├── scripts/               # 🆕 Helper scripts
│   │   ├── quick_eval_th.py  # Thai evaluation runner
│   │   ├── quick_eval_en.py  # English evaluation runner
│   │   ├── quick_print_th.py # Thai results viewer
│   │   ├── quick_print_en.py # English results viewer
│   │   ├── print_eval_summary.py
│   │   ├── test_api_call.py
│   │   └── test_api_payload.py
│   └── results/               # 🆕 Evaluation results
│       ├── th/               # Thai results
│       └── en/               # English results
│
├── description_evaluation/     # Description quality evaluation
│   └── README.md
│
└── qa_evaluation/             # Q&A evaluation
    └── README.md
```

## 🚀 Quick Start

### Option 1: Using Launcher (Recommended)
```bash
cd backend/evaluation
python launcher.py
```
The launcher provides an interactive menu for all evaluation tasks.

### Option 2: Direct Script Execution

#### Thai Evaluation
```bash
cd backend/evaluation/summary_evaluation
python scripts/quick_eval_th.py    # Run evaluation
python scripts/quick_print_th.py   # View results
```

#### English Evaluation
```bash
cd backend/evaluation/summary_evaluation
python scripts/quick_eval_en.py    # Run evaluation
python scripts/quick_print_en.py   # View results
```

## 📊 Evaluation Metrics

### 1. Faithfulness (QAG Scorer)
- Measures accuracy based on actual data
- Uses Question-Answer-Generation approach
- Location: `metrics/faithfulness.py`

### 2. Conciseness (G-Eval)
- Evaluates brevity and lack of redundancy
- Uses LLM-as-a-Judge with Chain-of-Thought
- Location: `metrics/conciseness.py`

### 3. Completeness (G-Eval)
- Checks if all important recommendations are included
- Compares against rule-based recommendations
- Location: `metrics/completeness.py`

### 4. Helpfulness (G-Eval + CoT)
- Assesses practical value and actionability
- Focuses on clarity and patient understanding
- Location: `metrics/helpfulness.py`

## 🌐 Language Support

The system supports both **Thai** and **English** evaluation:
- **Criteria files**: `criteria/th/` and `criteria/en/`
- **Prompts**: Language-specific prompts in each metric
- **Results**: Separate folders for each language

## ⚙️ Configuration

### Environment Variables
Required in `backend/.env`:
```bash
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### Script Configuration
Edit parameters in `scripts/quick_eval_th.py` or `scripts/quick_eval_en.py`:
- `SAMPLE_SIZE`: Number of test cases (default: 100)
- `VERBOSE`: Show detailed reasoning (default: True)
- `OUTPUT_DIR`: Results directory
- `LANGUAGE`: "th" or "en"

### Metric Weights
Default weights (customizable via `--weights`):
```python
{
    "faithfulness": 0.35,   # Most important
    "completeness": 0.35,   # Most important
    "conciseness": 0.15,
    "helpfulness": 0.15
}
```

## 📖 Documentation

- **Evaluation Guide**: `EVALUATION_GUIDE.md` - Overall methodology
- **Criteria Guide**: `criteria/README.md` - How criteria work
- **Summary Evaluation**: `summary_evaluation/README.md` - Detailed usage

## 🔧 Advanced Usage

### Custom Evaluation
```bash
cd summary_evaluation
python evaluate_summary.py \
  --csv generated_test_cases.csv \
  --sample 50 \
  --language en \
  --verbose \
  --weights '{"faithfulness": 0.4, "completeness": 0.4}'
```

### Generate Test Data
```bash
cd summary_evaluation
python generate_test_data.py
```

### Test API
```bash
cd summary_evaluation/scripts
python test_api_call.py
```

## 📈 Results

Results are saved in `summary_evaluation/results/`:
- `th/` - Thai evaluation results
  - `evaluation_results_YYYYMMDD_HHMMSS.json`
  - `evaluation_reasons_YYYYMMDD_HHMMSS.json`
  - `evaluation_summary_YYYYMMDD_HHMMSS.json`
- `en/` - English evaluation results (same structure)

## 🆕 Recent Changes

**February 2026 - Restructuring**:
- ✅ Created `criteria/` folder for evaluation criteria
- ✅ Created `scripts/` folder for helper scripts
- ✅ Reorganized `results/` into `th/` and `en/` subfolders
- ✅ Renamed scripts for clarity (`quick_eval_th.py`, `quick_eval_en.py`)
- ✅ Added `launcher.py` for easy access to all scripts
- ✅ Updated all path references

## 🔄 Migration Notes

If you have old results in `results_th/` or `results_en/`, they have been moved to:
- `results_th/` → `summary_evaluation/results/th/`
- `results_en/` → `summary_evaluation/results/en/`

Old criteria files have been moved to:
- `evaluation_criteria_*.txt` → `criteria/th/*.txt`
- `evaluation_criteria_*_en.txt` → `criteria/en/*.txt`

## 📝 Requirements

- Python 3.8+
- DeepSeek API key
- Required packages: see `backend/requirements.txt`

## 🤝 Contributing

When adding new metrics or criteria:
1. Add metric class to `metrics/`
2. Add criteria files to `criteria/th/` and `criteria/en/`
3. Update metric imports in `metrics/__init__.py`
4. Update evaluation pipeline in `summary_evaluation/evaluate_summary.py`
5. Update documentation
