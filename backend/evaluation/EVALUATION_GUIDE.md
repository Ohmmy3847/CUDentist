# LLM Evaluation Framework

Based on [Confident AI's comprehensive LLM evaluation guide](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation).

## Overview

This evaluation system uses state-of-the-art LLM evaluation techniques to assess the quality of medical recommendation summaries for post-operative jaw surgery patients.

## Evaluation Framework

### The 5-Metric Rule

Following Confident AI's best practices, we use **6 metrics** (slightly above the recommended 5, due to the medical domain's complexity):

#### Generic Metrics (3)
1. **Faithfulness** - QAG Scorer
2. **Conciseness** - G-Eval  
3. **Answer Relevancy** - RAG Metric

#### Custom Domain-Specific Metrics (3)
4. **Medical Correctness** - G-Eval with medical safety criteria
5. **Contextual Relevancy** - Context-aware evaluation
6. **Helpfulness** - G-Eval with Chain-of-Thought

## Metric Details

### 1. Faithfulness (QAG Scorer)
**Type**: Question-Answer Generation based scoring  
**Purpose**: Prevents hallucination by verifying factual accuracy

**How it works**:
1. Extract all claims from the LLM output
2. For each claim, verify against input data and expected recommendations
3. Calculate proportion of truthful claims

**Score**: 0.0 - 1.0  
**Threshold**: 0.7

**Why QAG?**: 
- More reliable than direct LLM scoring
- Uses LLM's reasoning without arbitrary score generation
- Achieves both accuracy and reliability

### 2. Conciseness (G-Eval)
**Type**: G-Eval with Chain-of-Thought evaluation  
**Purpose**: Ensures summaries are brief, non-redundant, and well-organized

**How it works**:
1. Generate evaluation steps via CoT
2. Assess length, redundancy, and grouping
3. Score from 1-5, normalized to 0-1

**Score**: 0.0 - 1.0  
**Threshold**: 0.7

**Why G-Eval?**:
- Flexible evaluation criteria
- Better alignment with human judgment than statistical methods
- Can handle subjective quality assessment

### 3. Answer Relevancy (RAG-style)
**Type**: Sentence-level relevancy assessment  
**Purpose**: Ensures output addresses patient symptoms concisely and informatively

**How it works**:
1. Split output into sentences
2. For each sentence, verify relevance to patient symptoms
3. Calculate proportion of relevant sentences

**Score**: 0.0 - 1.0  
**Threshold**: 0.7

**Why this metric?**:
- Similar to RAG answer relevancy but adapted for medical recommendations
- Removes unnecessary/irrelevant information
- Ensures focused, patient-specific guidance

### 4. Medical Correctness (G-Eval with Safety Focus)
**Type**: G-Eval with 3-dimensional medical safety assessment  
**Purpose**: Ensures recommendations are medically safe, correct, and appropriate

**Evaluation Dimensions**:
1. **Safety** (Critical): No dangerous recommendations
2. **Correctness**: Aligns with medical guidelines
3. **Appropriateness**: Suitable for symptom severity and context

**Score**: 0.0 - 1.0  
**Threshold**: 0.7

**Why this matters**:
- Patient safety is paramount
- Prevents harmful medical advice
- Ensures compliance with standard of care

### 5. Contextual Relevancy
**Type**: Multi-factor contextual assessment  
**Purpose**: Evaluates appropriateness of recommendations to patient context

**Evaluation Factors**:
1. **Symptom-Specific** (40%): Matches symptom severity
2. **Procedure-Specific** (30%): Tailored to surgery type
3. **Time-Appropriate** (30%): Suitable for recovery phase

**Score**: 0.0 - 1.0  
**Threshold**: 0.7

**Why contextual?**:
- Medical advice must be personalized
- Same symptom requires different care based on procedure
- Recovery timeline matters

### 6. Helpfulness (G-Eval with CoT)
**Type**: G-Eval evaluating actionability and usefulness  
**Purpose**: Ensures recommendations actually help patients

**Evaluation Criteria**:
1. **Actionability**: Clear, implementable steps
2. **Clarity**: Easy to understand
3. **Completeness**: All necessary information included
4. **Reassurance**: Reduces anxiety, builds confidence

**Score**: 0.0 - 1.0  
**Threshold**: 0.7

**Why helpfulness?**:
- Technically correct advice isn't useful if patient can't follow it
- Patient empowerment and self-care are key outcomes
- Reduces unnecessary hospital visits

## Scoring Methods Explained

### G-Eval (Form-Filling Paradigm)
Based on the paper ["NLG Evaluation using GPT-4 with Better Human Alignment"](https://arxiv.org/pdf/2303.16634.pdf)

**Process**:
1. Generate evaluation steps via Chain-of-Thought
2. Use generated steps to score output (1-5)
3. Normalize to 0-1 scale

**Advantages**:
- High correlation with human judgment
- Flexible criteria definition
- Semantic understanding of outputs

**Used in**: Conciseness, Medical Correctness, Helpfulness

### QAG (Question-Answer Generation)
Confident AI's recommended approach for objective evaluation

**Process**:
1. Extract verifiable claims from output
2. Generate yes/no questions for each claim
3. Verify against reference data
4. Calculate proportion of truthful claims

**Advantages**:
- Reliable (deterministic scoring)
- Accurate (leverages LLM reasoning)
- No arbitrary score generation

**Used in**: Faithfulness

### LLM-as-a-Judge
General approach where LLM evaluates outputs using natural language rubrics

**Advantages**:
- Best method for complex, nuanced evaluation
- Can understand semantics and context
- More accurate than traditional metrics (BLEU, ROUGE)

**Disadvantages**:
- Can be inconsistent (requires proper prompting)
- Needs techniques like G-Eval for reliability

## Why Not Traditional Metrics?

### BLEU, ROUGE, METEOR ❌
**Problem**: Statistical methods don't capture semantic nuance
- Can't understand medical meaning
- Fail on paraphrased but correct advice
- Don't evaluate safety or helpfulness

### Embedding Similarity (BERTScore) ❌
**Problem**: Semantic similarity ≠ correctness
- Similar text can be medically wrong
- Doesn't catch subtle errors
- No safety assessment

### Why LLM-Evals? ✅
- Understand medical context
- Assess safety and appropriateness
- Flexible evaluation criteria
- Better correlation with expert judgment

## Usage

### Run Evaluation
```bash
cd backend/evaluation
python evaluate_summary.py --csv generated_test_cases.csv --sample 10
```

### Arguments
- `--csv`: Input test cases CSV file
- `--sample`: Number of cases to evaluate (default: all)
- `--output`: Output directory for results

### Output Files
1. **evaluation_results_[timestamp].csv**: Detailed per-case scores
2. **evaluation_summary_[timestamp].json**: Aggregate statistics

### Example Output
```json
{
  "total_cases": 50,
  "pass_rate": 0.88,
  "average_scores": {
    "faithfulness": 0.85,
    "conciseness": 0.82,
    "answer_relevancy": 0.87,
    "medical_correctness": 0.91,
    "contextual_relevancy": 0.84,
    "helpfulness": 0.83,
    "overall": 0.85
  }
}
```

## Threshold Settings

All metrics use **0.7 threshold** (70%) as the minimum passing score:
- **0.9 - 1.0**: Excellent
- **0.7 - 0.89**: Good (Passes)
- **0.5 - 0.69**: Needs Improvement (Fails)
- **0.0 - 0.49**: Poor (Fails)

## Metric Selection Strategy

Following Confident AI's guidance:

### DO ✅
- Use 1-2 custom metrics specific to medical domain
- Use 2-3 generic metrics for general quality
- Keep total metrics ≤ 6 for focus
- Mix subjective (G-Eval) and objective (QAG) methods

### DON'T ❌
- Use too many metrics (dilutes focus)
- Rely only on generic metrics (misses domain specifics)
- Use only statistical methods (misses semantic meaning)
- Ignore reliability (use proper LLM-Eval techniques)

## References

1. [LLM Evaluation Metrics: Everything You Need](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation) - Confident AI
2. [G-Eval Paper](https://arxiv.org/pdf/2303.16634.pdf) - NLG Evaluation using GPT-4
3. [Why LLM-as-a-Judge is the Best Method](https://www.confident-ai.com/blog/why-llm-as-a-judge-is-the-best-llm-evaluation-method) - Confident AI
4. [DeepEval Framework](https://github.com/confident-ai/deepeval) - Open-source LLM evaluation

## Future Improvements

### Potential Additions
1. **RAG Contextual Precision**: If we add retrieval from knowledge base
2. **Toxicity/Bias**: For responsible AI (currently not needed for medical domain)
3. **Multi-turn Metrics**: If we implement chatbot functionality

### Monitoring
- Track metric scores over time
- A/B test prompt variations
- Compare with human expert ratings
- Continuous improvement based on real patient feedback

---

**Built with**: DeepEval, Google Gemini 2.0 Flash, LangChain  
**Evaluation Approach**: LLM-as-a-Judge with G-Eval and QAG scorers  
**Domain**: Post-operative jaw surgery patient care
