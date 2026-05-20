# Senior Project — Dental Post-Op Chatbot

RAG-based chatbot สำหรับให้คำแนะนำหลังผ่าตัดทันตกรรม (ภาษาไทย/อังกฤษ)

---

## Architecture

```
User input
  → Symptom Mapping  (bge-m3 top-5 + strict LLM classify, precision=1)
  → Risk Assessment  (rule-based)
  → RAG Q&A          (hybrid search → LLM answer)
```

- **Backend**: FastAPI (`risk_service_api/app/`)
- **Frontend**: Next.js (`frontend/`)
- **Vector DB**: ChromaDB (`risk_service_api/data/chroma_db/`)
- **Embedding**: `BAAI/bge-m3` via Together AI (~$0.008/1M tokens)
- **LLM**: DeepSeek-V3 (`deepseek-chat`) — ถูกสุดใน tier เดียวกัน ($0.27/$1.10 per 1M tokens)

### Key service paths
- `risk_service_api/app/services/symptom/` — symptom mapping pipeline
- `risk_service_api/app/services/rag/` — retrieval + answer generation
- `risk_service_api/app/services/risk/` — rule-based risk assessment
- `risk_service_api/app/services/common/` — shared utilities

---

## Evaluation Framework

```
eval/
├── datasets/
│   ├── eval_symptom.json       # 62 items (52 positive + 10 negative)
│   ├── eval_qa_curated.json    # 20 curated QA (key_points verified จาก corpus)
│   ├── eval_qa_golden.json     # 16 golden QA (จากงานวิจัย, มี relevant_sources)
│   └── eval_risk_summary.json  # 25 risk assessment test cases
├── experiments/
│   ├── exp1_embedding.py       # Symptom mapping: embedding model comparison
│   ├── exp2_symptom.py         # Symptom full pipeline test
│   ├── exp3_risk_summary.py    # Risk assessment eval
│   ├── exp4_qa_end2end.py      # End-to-end QA coverage (MAIN)
│   ├── exp5_qa_golden.py       # Golden set QA eval
│   ├── exp6_retrieval.py       # Retrieval quality (แยกจาก generation)
│   ├── exp7_chunking.py        # Chunking strategy ablation (4 configs)
│   ├── exp8_hybrid.py          # Hybrid search weight ablation (6 configs)
│   └── exp9_llm_comparison.py  # LLM model comparison (DeepSeek vs Gemini vs Llama)
├── metrics/
│   ├── retrieval.py            # P@K, R@K, MRR, nDCG
│   ├── generation.py           # ROUGE-L, BLEU, BERTScore
│   └── llm_judge.py            # LLM-as-Judge (answer + retrieval + summary)
├── results/
│   └── v{N}[_p{P}][_D{D}]/    # version / prompt variant / dataset variant
└── run_experiments.py          # Entry point: python eval/run_experiments.py --exp N
```

**Recommended order**: `1 → 2 → 3 → 6 → 7 → 8 → 9 → 4 → 5`
- Symptom (1→2) → Risk (3) → Retrieval + embedding (6) → Ablation (7→8) → LLM (9) → E2E QA (4→5)

**Version naming convention**: `v{N}` = config version, `_p{P}` = prompt variant, `_D{D}` = dataset variant

---

## Experiment History

### Exp1 — Symptom Mapping (Embedding Model Selection)

**Dataset**: `eval/datasets/eval_symptom.json`
- 52 positive items (Thai colloquial → canonical symptom label)
- 10 negative items (should_match=False, non-symptoms ที่ต้องปฏิเสธ)
- Difficulty: easy / medium / hard (ไม่มี keyword ตรงๆ เลย)

**Key discovery: Instruction mismatch**
- e5-large-instruct / qwen3-emb ใช้ `embed_query()` (prepends instruction) สำหรับ query แต่ `embed_documents()` (ไม่มี instruction) สำหรับ document → asymmetric embedding space → cosine sim ต่ำผิดปกติ
- **Fix**: ใช้ `_sym` cache — เรียก `embed_query()` ทั้ง query และ document (symmetric) เมื่อ `has_instruction=True`
- bge-m3 ไม่มี instruction → ไม่กระทบ

**Results (v13_p3_D2, symmetric embedding)**:

| Model | top1_acc | avg_sim+ | P@0.83 |
|-------|----------|----------|--------|
| e5-large-instruct | 0.865 | 0.958 | 1.000 (FP=0) |
| **bge-m3** | **0.885** | **0.875** | **1.000 (FP=0, TP=31)** |
| qwen3-emb | 0.962 | 0.843 | 1.000 (FP=0, TP=37) |

**Decision: ใช้ bge-m3 เป็น retriever + strict LLM classify ทุก case**
- Refactored: ตัด threshold ออกทั้งหมด → ทุก query ผ่าน LLM classify เสมอ
- Pipeline: top-5 candidates (cosine sim) → strict LLM classify → accept or reject
- Precision=1.0 target: LLM prompt ออกแบบให้ reject เมื่อไม่แน่ใจ (false rejection ดีกว่า false match)
- qwen3-emb ดีกว่าในแง่ top-1 accuracy แต่ overkill (8B, API latency, 4096-dim)
- **เหตุผลสำคัญ**: map ผิดอันตรายกว่า reject (wrong symptom → wrong risk flow)

**Threshold analysis**: `eval/results/exp1_threshold_analysis.py`
- Output: TP/FP/FN/TN + Precision/Recall/F1/Acc/FPR per threshold
- `← neg leak` marker เมื่อ FPR > 0

---

### Exp4 — End-to-End QA Coverage

**Metric**: `coverage_rate` = สัดส่วน key points ที่ AI ตอบครบ (judge by LLM)

| Version | coverage | acc | help | หมายเหตุ |
|---------|----------|-----|------|---------|
| v9 | 0.754 | 0.97 | 1.00 | baseline |
| v10_p2 | **0.771** | **0.98** | 0.99 | **best so far** |
| v11 | 0.700 | 0.94 | 0.88 | + reranker (ms-marco-MiniLM-L-12-v2) |
| v11_p2_D2 | 0.708 | 0.96 | 0.99 | — |
| v12 | 0.700 | 0.96 | 0.89 | + reranker (bge-reranker-v2-m3) |

**Reranker conclusion**: ทั้ง ms-marco และ bge-reranker ไม่ช่วยเพิ่ม coverage
- ms-marco: English-only → hurt Thai
- bge-reranker-v2-m3: multilingual แต่ coverage ไม่เพิ่ม
- สาเหตุน่าจะเป็น bottleneck อยู่ที่ document content ไม่ครบ ไม่ใช่ ranking
- **ตัดสินใจ: ไม่ใส่ reranker ใน pipeline**

---

### Exp6 — Retrieval Quality + RAG Embedding Comparison

**ทำไมต้องมี**:
1. Exp1 เทียบ embedding สำหรับ symptom (short→short) แต่ RAG เป็นคนละ task → ต้องเทสแยก
2. ต้องวัดทั้ง traditional retrieval metrics และ LLM-based metrics

**Models**: bge-m3 (baseline), e5-large-instruct, qwen3-emb — เหมือน Exp1 แต่วัดบน RAG

**Design**: Same chunks (recursive 1500) → embed 3 ครั้ง → hybrid search → evaluate

**Metrics (2 ชุด)**:
- Traditional (จาก relevant_sources ground truth): P@15, R@15, MRR, nDCG@15
- LLM Judge: groundedness, completeness, relevance

**Dataset**: `eval_qa_golden.json` (16 items, มี relevant_sources + expected_key_points)

---

### Exp7 — Chunking Strategy Ablation

**ทำไมต้องมี**: example_project เปรียบเทียบ Recursive vs Hybrid chunking พร้อมวัด chunk stats + retrieval quality
เราต้องมีเหตุผลว่าทำไมเลือก recursive 1500 chars

**Configs** (จาก `eval/config.py`):
- A: Recursive 1000 chars, overlap 150
- B: Recursive 1500 chars, overlap 200 (baseline ✅)
- C: Recursive 2500 chars, overlap 300
- D: Fixed 1500 chars, overlap 200

**Metrics**: chunk count, avg/std/min/max size + retrieval quality (LLM judge)

---

### Exp8 — Hybrid Search Weight Ablation

**ทำไมต้องมี**: example_project ทดสอบ hybrid search ว่าดีกว่า dense-only/sparse-only อย่างไร

**Configs** (6 ชุด): dense_only → dense_0.8 → dense_0.6 (baseline ✅) → equal → bm25_0.6 → bm25_only

**Metrics**: retrieval quality (groundedness, completeness, relevance) per weight config

---

### Exp9 — LLM Model Comparison

**ทำไมต้องมี**: ต้องตอบได้ว่า "ทำไมใช้ DeepSeek ไม่ใช่ Gemini Flash หรือ Llama?"

**Models ที่ทดสอบ**:
| Model | Provider | Price (in/out per 1M) |
|-------|----------|----------------------|
| DeepSeek-V3 (baseline ✅) | DeepSeek | $0.27 / $1.10 |
| Gemini 2.0 Flash | Google | $0.10 / $0.40 |
| Llama 3.3 70B | Together AI | $0.88 / $0.88 |

**Design**: Retrieval pipeline เหมือนกันทุก model (hybrid search → same chunks) ต่างกันแค่ LLM ที่ generate คำตอบ → วัด generation quality ตรงๆ

**Metrics** (เหมือน Exp4 — binary per-point judge):
- coverage_rate: สัดส่วน key_points ที่คำตอบครอบคลุม (0–1) ← PRIMARY
- accuracy: ข้อมูลที่กล่าวถึงถูกต้อง (0–1)
- helpfulness: ตอบได้ชัดเจน นำไปปฏิบัติได้ (0–1)

**Dataset**: `eval_qa_curated.json` (20 items)

**Results**: ยังไม่รัน — รอ v14

---

## Current State (as of 2026-03-23)

### ทำเสร็จแล้ว
- [x] Symptom mapping pipeline พร้อม bge-m3 + strict LLM classify (refactored: ตัด threshold ทั้งหมด)
- [x] Exp1 dataset hardened — 62 items, colloquial Thai, no exact-match keywords
- [x] Symmetric embedding fix สำหรับ instruction-based models
- [x] Threshold analysis พร้อม FPR column + neg leak detection
- [x] ทดลอง reranker (ms-marco + bge-reranker-v2-m3) → ไม่ช่วย
- [x] Rule-based recommendation (refactored จาก LLM เป็น rulebase)
- [x] Exp6/7/8 evaluation code — retrieval quality + chunking ablation + hybrid weight ablation
- [x] Exp9 LLM comparison code — DeepSeek vs Gemini Flash vs Llama 3.3 70B
- [x] Exp6 รวม RAG embedding comparison + P@K R@K MRR nDCG (ใช้ eval_qa_golden.json)
- [x] Together AI integration — embedding provider (ถูกกว่า OpenRouter), LLM provider (สำหรับ Llama)
- [x] Factory pattern รองรับ Together AI ทั้ง LLM และ Embedding

### กำลังทำ / ยังเปิดอยู่
- [ ] eval_symptom.json id 61-62 ต้องเปลี่ยนเป็น `should_match=False` (คอแห้ง ≠ ระคายเคืองคอ — คนละอย่างกัน)
- [ ] Exp2 — full pipeline test bge-m3 + strict LLM classify
- [ ] หา bottleneck ของ coverage_rate (stuck at ~0.77) — น่าจะเป็น doc completeness
- [ ] รัน Exp 1-9 ทั้งหมด save เป็น v14 แล้วบันทึกผลลง CLAUDE.md

### Known Issues
- คอแห้ง (dry throat) pipeline map ไปที่ "ปากแห้ง" → ต้องเป็น should_match=False ใน dataset
- coverage_rate หยุดอยู่ที่ 0.77 แม้จะปรับ config หลายอย่าง — bottleneck น่าจะเป็น doc completeness

---

## Config Reference

```python
# risk_service_api/app/core/config.py
EMBEDDING_MODEL = "BAAI/bge-m3"       # exp1 decision
LLM = "deepseek-chat"                 # exp9 comparison (cheapest in tier)
EMBEDDING_PROVIDER = "together"        # cheapest (~$0.008/1M tokens)
INITIAL_K = 50                         # hybrid search recall pool
FINAL_K = 15                           # chunks sent to LLM
# Symptom: top-5 candidates → strict LLM classify (no threshold)
```

---

## Running Experiments

```bash
# Run all experiments, save to v14
python eval/run_experiments.py --all --version v14

# Run specific experiment(s)
python eval/run_experiments.py --exp 1       # symptom embedding selection
python eval/run_experiments.py --exp 4       # end-to-end QA (MAIN)
python eval/run_experiments.py --exp 9       # LLM model comparison
python eval/run_experiments.py --exp 6 7 8   # all ablation studies
python eval/run_experiments.py --list        # list all experiments

# Threshold analysis for exp1
python eval/results/exp1_threshold_analysis.py

# Quick test (1 case)
python risk_service_api/scripts/test_symptom_mapping.py
```
