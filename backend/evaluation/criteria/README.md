# Evaluation Criteria

This directory contains evaluation criteria files for LLM-as-a-Judge metrics in both Thai and English.

## Structure

```
criteria/
├── th/                      # Thai evaluation criteria
│   ├── conciseness.txt     # Conciseness evaluation steps
│   ├── completeness.txt    # Completeness evaluation steps
│   └── helpfulness.txt     # Helpfulness evaluation steps
└── en/                      # English evaluation criteria
    ├── conciseness.txt     # Conciseness evaluation steps
    ├── completeness.txt    # Completeness evaluation steps
    └── helpfulness.txt     # Helpfulness evaluation steps
```

## Usage

These criteria files are automatically loaded by the metrics classes in `../metrics/`:
- `ConcisenessMetric` loads from `th/conciseness.txt` or `en/conciseness.txt`
- `CompletenessMetric` loads from `th/completeness.txt` or `en/completeness.txt`
- `HelpfulnessMetric` loads from `th/helpfulness.txt` or `en/helpfulness.txt`

The language is selected via the `language` parameter when initializing metrics.

## Criteria Content

Each criteria file contains:
1. **Scoring rubric** - Clear score definitions (1-5 or 0-10)
2. **Evaluation steps** - Chain-of-thought reasoning steps
3. **Examples** - Good and bad examples with explanations
4. **Special considerations** - Domain-specific guidelines

## Modifying Criteria

To modify evaluation criteria:
1. Edit the appropriate `.txt` file
2. Maintain consistent structure (scoring rubric, steps, examples)
3. Test with sample evaluations to ensure LLM understands the criteria
4. Clear cached criteria by deleting and regenerating if structure changes significantly
