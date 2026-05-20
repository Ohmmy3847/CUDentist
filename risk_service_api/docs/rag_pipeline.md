# RAG Pipeline Documentation

ระบบ Retrieval-Augmented Generation สำหรับตอบคำถามผู้ป่วยหลังทำหัตถการทันตกรรม

---

## ภาพรวม

```
┌─────────────────────────────────────────────────────────────────────┐
│                         2 Phase หลัก                                │
│                                                                     │
│   Phase 1: INGESTION        Phase 2: QUERY (Runtime)               │
│   (รันครั้งเดียว)              (ทุก request)                          │
│                                                                     │
│   Documents ──► ChromaDB    Patient Question ──► Answer             │
│                 BM25 Index                                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1 — Ingestion (`chunker.py`)

แปลงเอกสารทางทันตกรรมให้เป็น vector embeddings เก็บใน ChromaDB + BM25 index

```
risk_service_api/data/document/
├── markdown_th/   (*.md)
├── *.pdf
├── *.docx
└── *.txt
         │
         ▼
┌────────────────────┐
│  Extract Text      │  รองรับ: .pdf, .md, .txt, .docx
│  (heading-aware)   │  ตรวจจับ heading เพื่อรักษาโครงสร้าง
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  Recursive Chunk   │  CHUNK_MAX_CHARS = 1500 chars
│                    │  CHUNK_OVERLAP   = 200  chars
│                    │  แบ่งตาม section heading ก่อน
│                    │  ถ้า section ใหญ่เกิน → แบ่งตาม line boundary
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  Batch Embed       │  Model: BAAI/bge-m3 (via OpenRouter)
│  (OpenRouter API)  │  EMBED_BATCH_SIZE     = 30 texts/call
│                    │  MAX_CONCURRENT_EMBED = 5  parallel batches
└────────┬───────────┘
         │
         ├──────────────────────────────────────┐
         ▼                                      ▼
┌────────────────────┐              ┌───────────────────────┐
│  ChromaDB          │              │  BM25 Index           │
│  Collection:       │              │  (sparse retrieval)   │
│  "post_op_         │              │  bm25_index.pkl       │
│   propositions"    │              │  (บันทึกเป็น pickle)   │
│  CHROMA_ADD_BATCH  │              └───────────────────────┘
│  = 200 docs/batch  │
└────────────────────┘

Metadata ที่เก็บต่อ chunk:
  - source   : ชื่อไฟล์ต้นฉบับ
  - section  : หัวข้อ section ที่ chunk อยู่
```

**รัน Ingestion:**
```bash
cd risk_service_api
python -m app.services.rag.chunker          # ingest ใหม่ทั้งหมด
python -m app.services.rag.chunker --reset  # ลบแล้ว ingest ใหม่
```

---

## Phase 2 — Query Pipeline (`pipeline.py`)

```
Patient Input (question + patient_context)
         │
         ├─────────────────────────────────────────────┐
         │                                             │
         ▼ (async parallel)                            ▼
┌─────────────────────┐                  ┌─────────────────────────┐
│  Sufficiency Check  │                  │  retrieve_and_rerank()  │
│  (LLM call)         │                  │  (retrieval pipeline)   │
│                     │                  │  ดูรายละเอียดด้านล่าง    │
│  ถาม LLM ว่า         │                  └──────────┬──────────────┘
│  risk_assessment    │                             │
│  ตอบคำถามได้ไหม      │                             │
└──────────┬──────────┘                             │
           │                                        │
           ▼                                        │
     is_sufficient?                                 │
      YES ──────────────────────────────────────────┤
           │                                        │
           NO ◄──────────────────────────────────────┘
           │                retrieved_chunks
           ▼
┌─────────────────────┐
│  validate_chunks()  │  LLM กรอง chunk ที่ไม่เกี่ยวข้องออก
│  (parallel LLM)     │  YES = เก็บ / NO = ทิ้ง
└──────────┬──────────┘
           │  valid_chunks
           ▼
┌─────────────────────────────────────────────────────┐
│  Generate Answer                                    │
│  ChatPromptTemplate([NURSE_SYSTEM_PROMPT,           │
│                      NURSE_QA_TEMPLATE])            │
│                                                     │
│  Input fields:                                      │
│  - patient_profile  (procedures, days_post_op, ...) │
│  - current_symptoms (pain, swelling, ...)           │
│  - risk_level       (overall risk)                  │
│  - recommendations  (from rule engine)              │
│  - rag_context      (validated chunks joined)       │
│  - question         (original patient question)     │
└──────────┬──────────────────────────────────────────┘
           │
           ▼
     Final Answer
     + source: "rule_based" | "rag" | "Not enough information"
     + used_chunks: list
```

---

## Retrieval Sub-Pipeline (`retriever.py`)

```
question + patient_context
         │
         ▼
┌────────────────────────────┐
│  build_context_query()     │  เติม context ให้ query (deterministic, ไม่ใช้ LLM)
│                            │  "ผู้ป่วย [procedure] วันที่ [N] หลังผ่าตัด: [question]"
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│  rewrite_query()  [LLM]    │  ทำให้คำถามชัดเจน / formal ขึ้น
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│  decompose_query()  [LLM]  │  แยกคำถามที่มีหลาย intent
│                            │  "X และ Y?" → ["X?", "Y?"]
└────────────┬───────────────┘
             │  sub_queries[]
             ▼
┌────────────────────────────┐
│  expand_query()  [LLM]     │  สร้าง alternative queries
│                            │  เพื่อ improve recall
└────────────┬───────────────┘
             │  all_queries[]
             ▼
┌───────────────────────────────────────────────────┐
│  Hybrid Search (ต่อ query)                         │
│                                                   │
│  ChromaDB (dense)  ──┐  weight 0.6               │
│  BAAI/bge-m3         │                            │
│                      ├──► RRF merge ──► INITIAL_K │
│  BM25 (sparse)     ──┘  weight 0.4        = 50   │
│  bm25_index.pkl                                   │
└────────────┬──────────────────────────────────────┘
             │  ~50 docs (with duplicates across queries)
             ▼
┌────────────────────────────┐
│  deduplicate_docs()        │  fingerprint = first 150 chars
│                            │  ลบ near-duplicate chunks
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│  diversity_select()        │  MAX_CHUNKS_PER_SOURCE = 3
│                            │  ป้องกัน 1 ไฟล์ dominate ผลลัพธ์
└────────────┬───────────────┘
             │
             ▼
        RERANK_TOP_K = 15 chunks
        (ส่งต่อไป validate_chunks)

หมายเหตุ: FlashRank reranker ถูก disable
เพราะ model รองรับแค่ภาษาอังกฤษ → ลด MRR ภาษาไทย
```

---

## Validator (`validator.py`)

```
question + chunks[]
         │
         ▼  (parallel async — ทุก chunk พร้อมกัน)
┌──────────────────────────────────────────────┐
│  _validate_one(question, chunk)  [LLM × N]   │
│                                              │
│  Prompt: "chunk นี้เกี่ยวข้องกับคำถามไหม?"    │
│                                              │
│  เก็บ: สาเหตุ, อาการ, วิธีดูแล, คำแนะนำ,    │
│        ข้อมูลทางการแพทย์                      │
│                                              │
│  ทิ้ง: ชื่อเรื่อง, โฆษณา, ราคา, ลิงก์,        │
│        เนื้อหาไม่เกี่ยวข้อง                   │
│                                              │
│  Output: YES | NO                            │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
           valid_chunks[]  (เรียงลำดับเดิม)
```

---

## Context Builder (`context_builder.py`)

แปลง raw assessment data จาก frontend → structured patient_context

```
AssessmentRequest (from API)
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  build_patient_context(basic_info, assessment_data, │
│                        flows, risk_summary)         │
│                                                     │
│  ┌─ _build_patient_profile() ─────────────────────┐ │
│  │  procedures, days_post_op (คำนวณจาก surgery_date)│ │
│  │  lefort_sub_options, imf_wire, imf_wire_loops   │ │
│  │  special_icbg, special_ng_tube                 │ │
│  └────────────────────────────────────────────────┘ │
│                                                     │
│  ┌─ _build_current_symptoms() ───────────────────┐  │
│  │  14 fields: pain_score, swelling_status,      │  │
│  │  bleeding_status, fever_status, ...           │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  ┌─ _build_risk_assessment() ────────────────────┐  │
│  │  overall_risk, flows{}, recommendations[]     │  │
│  └───────────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
         patient_context (Dict)
         ├── patient_profile {}
         ├── current_symptoms {}
         └── risk_assessment {}
```

---

## Model Factory (`factory.py`)

```
                    ModelFactory
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
   get_llm(use_case)          get_embeddings(use_case)
          │                             │
    ┌─────┴──────┐               ┌──────┴───────┐
    │ use_case   │               │  use_case    │
    │            │               │              │
    │ "rag"      │──► DeepSeek   │  "rag"       │──► BAAI/bge-m3
    │ "summary"  │    /OpenRouter│              │    (OpenRouter)
    │ "symptom"  │               │  "symptom"   │──► bge-m3 หรือ
    │ "default"  │               │  "default"   │    ตาม settings
    └────────────┘               └──────────────┘

Provider ที่รองรับ (LLM): DeepSeek, OpenAI, Gemini, Ollama, OpenRouter
Provider ที่รองรับ (Embed): OpenRouter, OpenAI, Ollama
```

---

## ไฟล์และ Config สรุป

| ไฟล์ | หน้าที่ | LLM calls |
|------|---------|-----------|
| `chunker.py` | Ingestion: chunk → embed → store | 0 |
| `retriever.py` | Query rewrite, expand, hybrid search | 3 (rewrite, decompose, expand) |
| `validator.py` | กรอง chunk ที่ไม่เกี่ยวข้อง | N (parallel, 1 ต่อ chunk) |
| `pipeline.py` | Orchestrator: sufficiency check + generate | 2 (sufficiency, generate) |
| `context_builder.py` | แปลง API input → patient_context | 0 |
| `router.py` | จัด category ของคำถาม (optional) | 1 |
| `factory.py` | สร้าง LLM / Embeddings instances | - |

| Parameter | ค่า | ตำแหน่ง |
|-----------|-----|---------|
| CHUNK_MAX_CHARS | 1500 chars | chunker.py |
| CHUNK_OVERLAP | 200 chars | chunker.py |
| EMBED_BATCH_SIZE | 30 texts | chunker.py |
| INITIAL_K | 50 docs | retriever.py |
| RERANK_TOP_K | 15 docs | retriever.py |
| MAX_CHUNKS_PER_SOURCE | 3 chunks | retriever.py |
| Dense weight | 0.6 | retriever.py |
| BM25 weight | 0.4 | retriever.py |
| Collection name | "post_op_propositions" | chunker.py |
| Embedding model | BAAI/bge-m3 | factory.py / settings |

---

## Request Flow ทั้งหมด (End-to-End)

```
Frontend / API
     │  POST /assessment  (AssessmentRequest)
     ▼
assessment.py (router)
     │
     ├──► RuleEngine.evaluate_flow()   ← risk flows
     │
     ├──► summarize_all_risks()        ← LLM summary (ถ้า High/Medium)
     │
     └──► answer_patient_question()    ← RAG Q&A (ถ้ามี additional_questions)
               │
               ├── [parallel]
               │    ├── check_sufficiency()     [LLM]
               │    └── retrieve_and_rerank()
               │         ├── build_context_query()
               │         ├── rewrite_query()    [LLM]
               │         ├── decompose_query()  [LLM]
               │         ├── expand_query()     [LLM]
               │         └── hybrid search (ChromaDB + BM25)
               │
               ├── validate_chunks()  [LLM × N parallel]
               │
               └── generate answer   [LLM]
                    (NURSE_SYSTEM_PROMPT + NURSE_QA_TEMPLATE)
     │
     ▼
AssessmentResponse
  - risk_summary (overall_risk, summary text)
  - flow_results (per-symptom risks)
  - patient_answer (RAG answer ถ้ามีคำถาม)
```
