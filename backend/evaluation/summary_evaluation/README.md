# Summary Evaluation
LLM Summary (Phase 3) evaluation scripts and results

## Directory Structure

```
summary_evaluation/
├── README.md                    # This file
├── evaluate_summary.py         # Core evaluation engine
├── generate_test_data.py       # Test data generator
├── generated_test_cases.csv    # Test cases
├── scripts/                    # Helper scripts
│   ├── quick_eval_th.py       # Thai evaluation runner
│   ├── quick_eval_en.py       # English evaluation runner
│   ├── quick_print_th.py      # Thai results viewer
│   ├── quick_print_en.py      # English results viewer
│   ├── print_eval_summary.py  # Summary printer
│   ├── test_api_call.py       # API testing
│   └── test_api_payload.py    # Payload testing
└── results/                    # Evaluation results
    ├── th/                     # Thai evaluation results
    └── en/                     # English evaluation results
```

## Supported Languages

This evaluation system supports both **Thai (th)** and **English (en)** evaluation criteria.

## Quick Start

### Thai Version
```bash
# Run evaluation with Thai criteria
python scripts/quick_eval_th.py

# View results
python scripts/quick_print_th.py
```

### English Version
```bash
# Run evaluation with English criteria
python scripts/quick_eval_en.py

# View results
python scripts/quick_print_en.py
```

## Configuration

Edit the following parameters in `scripts/quick_eval_th.py` or `scripts/quick_eval_en.py`:
- `SAMPLE_SIZE`: Number of test cases (or `None` for all)
- `VERBOSE`: Show detailed reasoning
- `OUTPUT_DIR`: Results directory
  - Thai version: `../results/th`
  - English version: `../results/en`
- `LANGUAGE`: Evaluation criteria language (`"th"` or `"en"`)

## Evaluation Metrics

1. **Faithfulness** - Accuracy based on actual data (QAG scorer)
2. **Conciseness** - Brief, no redundancy (G-Eval)
3. **Completeness** - Comprehensive recommendations (G-Eval Gemini)
4. **Helpfulness** - Practical and actionable (G-Eval + CoT)

## Criteria Files

Evaluation criteria are stored in `../criteria/`:
- Thai criteria: `../criteria/th/` (conciseness.txt, completeness.txt, helpfulness.txt)
- English criteria: `../criteria/en/` (conciseness.txt, completeness.txt, helpfulness.txt)

## Advanced Usage

Run evaluation with custom parameters:
```bash
# Thai with custom sample size
python evaluate_summary.py --csv generated_test_cases.csv --sample 50 --language th

# English with verbose output
python evaluate_summary.py --csv generated_test_cases.csv --sample 100 --verbose --language en

# Custom weights
python evaluate_summary.py --weights '{"faithfulness": 0.4, "completeness": 0.4}' --language en
```

## Requirements

- Python 3.8+
- `DEEPSEEK_API_KEY` environment variable (in `backend/.env`)
- All metrics use DeepSeek
