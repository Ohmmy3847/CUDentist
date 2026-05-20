# 📋 รายงานสรุป Pipeline ทั้งหมดของระบบ CU Dentist (Backend)

> **จัดทำเมื่อ:** 14 มีนาคม 2569  
> **ระบบ:** CU Dentist - ระบบประเมินอาการหลังหัตถการทางทันตกรรมผ่าน LINE

---

## 1. ภาพรวมระบบ (System Overview)

ระบบ CU Dentist Backend ประกอบด้วย **3 Pipeline หลัก** ที่ทำงานร่วมกัน:

| Pipeline | หน้าที่ | ตำแหน่งไฟล์หลัก |
|---|---|---|
| **A. Symptom Mapping** | จับคู่อาการผู้ป่วย → ฐานข้อมูลอาการ | `app/services/symptom/mapping.py` |
| **B. Risk Classification** | ประเมินความเสี่ยงตาม Rule-Based | `app/services/risk/` |
| **C. RAG Q&A** | ตอบคำถามผู้ป่วยจากเอกสารทันตกรรม | `app/services/rag/` |

```
                        ┌──────────────────────────────────────┐
                        │        ผู้ป่วย (LINE OA)              │
                        └──────────┬───────────────────────────┘
                                   │ กรอกแบบประเมินอาการ
                                   ▼
              ┌────────────────────────────────────────────┐
              │              Frontend (Next.js)             │
              └─────────────┬──────────────────────────────┘
                            │ API Request
                            ▼
    ┌───────────────────────────────────────────────────────────┐
    │                    Backend (FastAPI)                       │
    │                                                           │
    │   ┌─────────────┐  ┌──────────────┐  ┌───────────────┐   │
    │   │ A. Symptom   │  │ B. Risk      │  │ C. RAG Q&A    │   │
    │   │    Mapping   │  │    Engine     │  │    Pipeline   │   │
    │   └──────┬──────┘  └──────┬───────┘  └───────┬───────┘   │
    │          │                │                   │            │
    │          ▼                ▼                   ▼            │
    │   ┌──────────┐   ┌────────────┐   ┌──────────────────┐   │
    │   │ ChromaDB │   │ Rule JSON  │   │    ChromaDB      │   │
    │   │(symptoms)│   │  Engine    │   │(post_op_props)   │   │
    │   └──────────┘   └────────────┘   │  + BM25 Index    │   │
    │                                   └──────────────────┘   │
    └───────────────────────────────────────────────────────────┘
```

---

## 2. Pipeline A: Symptom Mapping (การจับคู่อาการ)

### 2.1 วัตถุประสงค์
รับอาการจากผู้ป่วย (Free Text เช่น "ปวดหัว คลื่นไส้") แล้วจับคู่กับอาการมาตรฐานในระบบ (Canonical Symptoms) พร้อมส่งคืนระดับความเสี่ยงและคำแนะนำ

### 2.2 ฐานข้อมูล
- **Source:** `Custom_Symptom.csv` (34 อาการ)
- **Storage:** ChromaDB Collection ชื่อ `symptoms`
- **Embedding Model:** `intfloat/multilingual-e5-large` (ผ่าน OpenRouter API)
- **Distance Metric:** Cosine Similarity

### 2.3 Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│              Symptom Mapping Pipeline (3-Tier)                       │
└──────────────────────────────────────────────────────────────────────┘

  ผู้ป่วยพิมพ์:  "ปวดหัวมาก แล้วก็เวียนหัว คลื่นไส้นิดหน่อย"
                     │
                     ▼
  ┌──────────────────────────────────────┐
  │  Step 1: LLM Symptom Extraction     │
  │  (DeepSeek LLM)                     │
  │                                      │
  │  แยก Free Text → Symptom Phrases    │
  │  Input:  "ปวดหัวมาก แล้วก็เวียนหัว" │
  │  Output: ["ปวดหัวมาก",              │
  │           "เวียนหัว",               │
  │           "คลื่นไส้"]               │
  └──────────┬───────────────────────────┘
             │
             │  (แต่ละ Symptom Phrase ถูกส่งเข้า Step 2 แบบ Parallel)
             ▼
  ┌──────────────────────────────────────┐
  │  Step 2: Vector Search (Per Phrase)  │
  │  (ChromaDB + Cosine Similarity)     │
  │                                      │
  │  Embed phrase → query ChromaDB      │
  │  ดึง Top-5 Candidates มาเรียงตาม   │
  │  ค่า Similarity สูงสุด             │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  Step 3: 3-Tier Decision                                     │
  │                                                              │
  │  ┌────────────────────────────────────┐                      │
  │  │ Tier 1: Auto Accept               │                      │
  │  │ similarity ≥ 0.90                  │  ──→ ✅ จับคู่สำเร็จ │
  │  │ (ตรงกันชัดเจน ไม่ต้องถาม LLM)    │                      │
  │  └────────────────────────────────────┘                      │
  │                                                              │
  │  ┌────────────────────────────────────┐                      │
  │  │ Tier 2: LLM Arbitration           │                      │
  │  │ 0.70 ≤ similarity < 0.90          │  ──→ ถาม LLM ว่า    │
  │  │ (ไม่แน่ใจ ส่งให้ LLM ตัดสิน)     │      ตรงกันไหม?      │
  │  └────────────────────────────────────┘                      │
  │                                                              │
  │  ┌────────────────────────────────────┐                      │
  │  │ Tier 3: Reject                    │                      │
  │  │ similarity < 0.70                  │  ──→ ❌ ไม่พบอาการ  │
  │  │ (ห่างเกินไป ตัดทิ้ง)             │      ที่ตรงกัน       │
  │  └────────────────────────────────────┘                      │
  └──────────┬───────────────────────────────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Step 4: Deduplication              │
  │  รวมผลลัพธ์ + ตัดซ้ำ               │
  │  ส่งคืน: อาการที่ Match,            │
  │  ระดับเสี่ยง, คำแนะนำ              │
  └──────────────────────────────────────┘
```

### 2.4 Threshold ที่ใช้

| ค่า | ชื่อ | ความหมาย |
|---|---|---|
| 0.93 | `SINGLE_MATCH_THRESHOLD` | ถ้า Free Text ทั้งวลีตรงกับ Label เดียว ≥ 0.93 → ข้ามขั้นตอน LLM Extraction |
| 0.90 | `AUTO_ACCEPT_THRESHOLD` | ≥ 0.90 → Tier 1: Auto Accept |
| 0.70 | `LLM_THRESHOLD` | ≥ 0.70 → Tier 2: ส่งให้ LLM ตัดสิน |

---

## 3. Pipeline B: Risk Classification (การประเมินความเสี่ยง)

### 3.1 วัตถุประสงค์
ประเมินระดับความเสี่ยงของผู้ป่วยจากข้อมูลอาการที่กรอกมา โดยใช้ Rule-Based Engine ที่เป็น Deterministic (ให้ผลเหมือนเดิมทุกครั้ง)

### 3.2 Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│              Risk Classification Pipeline                 │
└──────────────────────────────────────────────────────────┘

  ข้อมูลจากแบบฟอร์ม (Assessment Data)
  เช่น pain_score=7, bleeding=true, fever=true
                     │
                     ▼
  ┌──────────────────────────────────────┐
  │  Step 1: Rule Engine                 │
  │  (flow_parser.py)                    │
  │                                      │
  │  ใช้ Decision Tree / Rule-Based     │
  │  ประเมินแต่ละ Flow:                 │
  │  - Pain Flow                         │
  │  - Swelling Flow                     │
  │  - Bleeding Flow                     │
  │  - Fever Flow                        │
  │  - Numbness Flow                     │
  │  - ฯลฯ                              │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Step 2: Summarizer                  │
  │  (summarizer.py)                     │
  │                                      │
  │  สรุป Overall Risk จากทุก Flow:     │
  │  - ต่ำ / ปานกลาง / สูง              │
  │  รวบรวม Recommendations ทั้งหมด     │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Output:                             │
  │  - overall_risk: "สูง"               │
  │  - per-flow risks: {...}             │
  │  - recommendations: [...]            │
  └──────────────────────────────────────┘
```

---

## 4. Pipeline C: RAG Q&A (ตอบคำถามจากเอกสาร)

### 4.1 วัตถุประสงค์
ตอบคำถามเพิ่มเติมของผู้ป่วย (เช่น "ผ่าฟันคุดต้องพักฟื้นกี่วัน?") โดยค้นหาข้อมูลจากเอกสารวิชาการทันตกรรม แล้วให้ LLM สรุปคำตอบในรูปแบบพยาบาลพูดคุย

### 4.2 โครงสร้างไฟล์

| ไฟล์ | หน้าที่ |
|---|---|
| `chunker.py` | แบ่งเอกสาร → Chunks + Embed → เก็บใน ChromaDB & BM25 |
| `retriever.py` | ค้นหา Chunks ที่เกี่ยวข้อง (Hybrid Search + Rerank) |
| `validator.py` | ตรวจสอบว่า Chunks ที่ได้มาเกี่ยวข้องจริงหรือไม่ |
| `context_builder.py` | สร้าง Patient Context จากข้อมูลแบบฟอร์ม |
| `pipeline.py` | ประสาน Pipeline ทั้งหมด → สร้างคำตอบสุดท้าย |
| `prompts.py` | System Prompt และ Template สำหรับ LLM |

### 4.3 ขั้นตอนที่ 1: Data Ingestion (ทำครั้งเดียวตอนเตรียมข้อมูล)

```
┌──────────────────────────────────────────────────────────────────────┐
│         Data Ingestion Pipeline (chunker.py)                         │
│         คำสั่ง: python -m app.services.rag.chunker --reset -y        │
└──────────────────────────────────────────────────────────────────────┘

  เอกสาร 149 ไฟล์ (PDF + Markdown)
  จากโฟลเดอร์ risk_service_api/data/document/
                     │
                     ▼
  ┌──────────────────────────────────────┐
  │  Step 1: Text Extraction             │
  │                                      │
  │  PDF  → PyMuPDF (fitz)              │
  │  MD   → Custom Parser + Cleaning    │
  │  TXT  → Line-based Parser           │
  │  DOCX → python-docx                 │
  │                                      │
  │  Markdown Cleaning:                  │
  │  - ตัด Navigation Header            │
  │  - ตัด Footer (Source, Scraped)     │
  │  - ตัดบรรทัดขยะ (โทร, โปรโมชั่น)   │
  │  - ลบ Markdown formatting (**,[]()) │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Step 2: Recursive Chunking          │
  │  (Section-Aware)                     │
  │                                      │
  │  แบ่งตามหัวข้อ (Heading) ของเอกสาร  │
  │  ถ้า Section ≤ 1500 chars → 1 chunk │
  │  ถ้า Section > 1500 chars → split   │
  │  ที่ขอบบรรทัด + overlap 200 chars   │
  │                                      │
  │  แต่ละ Chunk มี Header:             │
  │  [SOURCE: filename | SECTION: name] │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Step 3: Batch Embedding             │
  │  (intfloat/multilingual-e5-large)    │
  │                                      │
  │  → 2206 chunks                       │
  │  → ส่งเป็น Batch (30 texts/batch)   │
  │  → 5 parallel workers               │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Step 4: Store                       │
  │                                      │
  │  ChromaDB: post_op_propositions     │
  │      (Vector Index สำหรับ Dense)     │
  │                                      │
  │  BM25 Index: bm25_index.pkl         │
  │      (Keyword Index สำหรับ Sparse)  │
  └──────────────────────────────────────┘
```

### 4.4 ขั้นตอนที่ 2: Retrieval & Answer Generation (ทำทุกครั้งที่ผู้ป่วยถามคำถาม)

```
┌──────────────────────────────────────────────────────────────────────┐
│         RAG Q&A Pipeline (pipeline.py + retriever.py)                │
└──────────────────────────────────────────────────────────────────────┘

  คำถามผู้ป่วย: "ผ่าฟันคุดต้องพักฟื้นกี่วัน?"
  + Patient Context (จาก context_builder)
                     │
                     ▼
  ┌──────────────────────────────────────┐
  │  Step 0: Sufficiency Check           │
  │  (pipeline.py)                       │
  │                                      │
  │  ถาม LLM: "ข้อมูล Risk Assessment  │
  │  ที่มีอยู่ เพียงพอจะตอบคำถามนี้     │
  │  ได้หรือไม่?"                       │
  │                                      │
  │  YES → ข้าม RAG ไปตอบจาก Context   │
  │  NO  → เข้า Retrieval Pipeline ▼    │
  └──────────┬───────────────────────────┘
             │ (NO → ข้อมูลไม่พอ ต้องค้นหาเพิ่ม)
             ▼
  ┌──────────────────────────────────────┐
  │  Step 1: Query Rewriting (LLM #1)   │
  │  (retriever.py)                      │
  │                                      │
  │  ปรับปรุงคำถามให้ชัดเจนขึ้น         │
  │  + ใส่บริบทผู้ป่วยเข้าไป            │
  │                                      │
  │  "พักฟื้นกี่วัน?"                   │
  │  → "ผ่าฟันคุดต้องพักฟื้นกี่วัน     │
  │     และดูแลช่องปากอย่างไร"          │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Step 2: Query Decomposition (LLM#2)│
  │                                      │
  │  ตรวจสอบว่าคำถามมีหลายประเด็นไหม   │
  │  ถ้ามี → แยกเป็น Sub-queries        │
  │                                      │
  │  "พักฟื้นกี่วัน ดูแลยังไง?"         │
  │  → ["พักฟื้นหลังผ่าฟันคุดกี่วัน",  │
  │     "วิธีดูแลช่องปากหลังผ่าฟันคุด"] │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Step 3: Query Expansion (LLM #3)   │
  │  (Parallel สำหรับแต่ละ Sub-query)   │
  │                                      │
  │  สร้างคำค้นหาหลายรูปแบบ (3 แบบ/Q) │
  │  เช่น ใช้ศัพท์วิชาการ,             │
  │  ภาษาชาวบ้าน, มุมมองต่างกัน       │
  │                                      │
  │  เช่น: "ระยะเวลาพักฟื้นหลัง       │
  │  surgical extraction ฟันคุด"        │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Step 4: Hybrid Retrieval            │
  │  (Parallel สำหรับทุก Query)         │
  │                                      │
  │  ┌──────────────┐ ┌──────────────┐  │
  │  │ Dense Search │ │ Sparse Search│  │
  │  │ (ChromaDB)   │ │ (BM25)       │  │
  │  │ น้ำหนัก: 0.6 │ │ น้ำหนัก: 0.4│  │
  │  └──────┬───────┘ └──────┬───────┘  │
  │         └────────┬───────┘          │
  │                  ▼                   │
  │        EnsembleRetriever             │
  │     (รวมผลลัพธ์ถ่วงน้ำหนัก)        │
  │                                      │
  │  ดึงทั้งหมด: 30 docs/query          │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Step 5: Deduplication               │
  │                                      │
  │  ใช้ Fingerprint (150 ตัวอักษรแรก) │
  │  ตัด Chunks ที่ซ้ำกันออก            │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Step 6: FlashRank Reranking         │
  │                                      │
  │  จัดอันดับ Chunks ใหม่ตามความ       │
  │  เกี่ยวข้องกับคำถาม (Cross-Encoder) │
  │  ใช้ Rewritten Query เป็น Reference │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Step 7: Diversity Selection         │
  │  (MMR-like Greedy)                   │
  │                                      │
  │  เลือก Top-15 จาก Pool 40 ตัว      │
  │  ใช้ Trigram Jaccard ≤ 0.5 กรอง     │
  │  เอาเฉพาะ Chunks ที่มีเนื้อหา      │
  │  หลากหลาย ไม่ซ้ำกัน                │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Step 8: Sibling Enrichment          │
  │                                      │
  │  จาก Chunks ที่เลือกได้ →           │
  │  ดู Top-3 Source Documents           │
  │  แล้วดึง Chunks อื่นๆ จากเอกสาร   │
  │  เดียวกันมาเสริม (สูงสุด 10/source)│
  │                                      │
  │  → ได้ Context ที่ครอบคลุม          │
  │  จากเอกสารเดียวกันมากขึ้น          │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Step 9: Chunk Validation            │
  │  (validator.py - Parallel LLM)       │
  │                                      │
  │  ตรวจสอบทีละ Chunk (Parallel):      │
  │  "Chunk นี้มีข้อมูลที่เป็นประโยชน์ │
  │   ต่อการตอบคำถามหรือไม่?"           │
  │                                      │
  │  YES → เก็บไว้                       │
  │  NO  → ตัดทิ้ง (โฆษณา/ไม่เกี่ยว)  │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Step 10: Answer Generation          │
  │  (pipeline.py + prompts.py)          │
  │                                      │
  │  รวม Context ทั้งหมด:               │
  │  - Patient Profile (หัตถการ, วัน)   │
  │  - Current Symptoms (อาการ)         │
  │  - Risk Assessment (ความเสี่ยง)     │
  │  - RAG Context (Chunks ที่ Valid)    │
  │                                      │
  │  ส่งเข้า LLM พร้อม System Prompt   │
  │  ที่กำหนดให้ตอบเหมือนพยาบาล        │
  │  พูดคุยกับผู้ป่วยโดยตรง            │
  └──────────┬───────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────┐
  │  Output: คำตอบภาษาเดียวกับคำถาม     │
  │  + Source (rule_based / rag)          │
  │  + Used Chunks (สำหรับ Debug)        │
  └──────────────────────────────────────┘
```

---

## 5. เทคโนโลยีและโมเดลที่ใช้

### 5.1 LLM Models

| Use Case | Model | Provider |
|---|---|---|
| RAG (Query Rewriting, Expansion, Answer) | DeepSeek | OpenRouter / DeepSeek API |
| Symptom Extraction & Arbitration | DeepSeek | OpenRouter / DeepSeek API |
| Risk Summary | DeepSeek | OpenRouter / DeepSeek API |

### 5.2 Embedding Model

| Model | Dimension | Provider |
|---|---|---|
| `intfloat/multilingual-e5-large` | 1024 | OpenRouter API |

### 5.3 Reranker

| Model | ประเภท |
|---|---|
| FlashRank | Cross-Encoder (Local, ไม่ต้องใช้ API) |

### 5.4 Database & Storage

| ชื่อ | ประเภท | ข้อมูล |
|---|---|---|
| ChromaDB `symptoms` | Vector DB | 34 อาการมาตรฐาน |
| ChromaDB `post_op_propositions` | Vector DB | 2,206 chunks จากเอกสาร 149 ไฟล์ |
| BM25 Index (`bm25_index.pkl`) | Keyword Index | 2,206 entries (Sparse Retrieval) |

---

## 6. Parameter สำคัญ

### 6.1 Chunking (Data Ingestion)

| Parameter | ค่า | ความหมาย |
|---|---|---|
| `CHUNK_MAX_CHARS` | 1,500 | จำนวนตัวอักษรสูงสุดต่อ Chunk |
| `CHUNK_OVERLAP` | 200 | ตัวอักษรที่ซ้อนทับกันระหว่าง Chunks |
| `EMBED_BATCH_SIZE` | 30 | จำนวน texts ต่อ 1 API call |
| `MAX_CONCURRENT_EMBED` | 5 | จำนวน workers ที่ Embed พร้อมกัน |

### 6.2 Retrieval (Search)

| Parameter | ค่า | ความหมาย |
|---|---|---|
| `INITIAL_K` | 30 | จำนวน docs ที่ดึงจาก ChromaDB ต่อ 1 query |
| `RERANK_TOP_K` | 15 | จำนวน docs ที่เก็บหลัง Reranking |
| `RERANK_POOL` | 40 | ขนาด pool สำหรับ Diversity Selection |
| `NUM_EXPANSIONS` | 3 | จำนวน Expanded Queries ต่อ 1 คำถาม |
| `DIVERSITY_THRESH` | 0.5 | Threshold สำหรับกรอง Chunks ที่ซ้ำกัน |
| `SIBLING_BONUS` | 10 | จำนวน Sibling Chunks สูงสุดที่ดึงเพิ่ม |
| Hybrid Weights | 0.6 Dense / 0.4 BM25 | สัดส่วน Dense vs Sparse Retrieval |

---

## 7. คำสั่งที่ใช้บ่อย

### 7.1 Ingestion (สร้าง/อัพเดต Database)

```bash
# Ingest เอกสาร RAG (ลบของเก่า + สร้างใหม่)
python -m app.services.rag.chunker --reset -y

# Ingest อาการ Symptom (ลบของเก่า + สร้างใหม่)
python app/services/symptom/mapping.py --ingest --reset -y
```

### 7.2 Testing

```bash
# ทดสอบ RAG Pipeline
python scripts/test_context_rag.py

# ทดสอบ Symptom Mapping
python app/services/symptom/mapping.py --test "คอหัก"

# ส่อง Database ข้างใน
python scripts/inspect_chromadb.py
```

---

## 8. Full System Flow (ภาพรวมการทำงานตั้งแต่ต้นจนจบ)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Full Patient Assessment Flow                         │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌───────────┐
  │ ผู้ป่วย    │  กรอกแบบประเมินอาการผ่าน LINE
  └─────┬─────┘
        │
        ▼
  ┌───────────────────────┐
  │ 1. Symptom Input      │  ผู้ป่วยรายงานอาการ
  │    (Free Text)        │  เช่น "ปวดบริเวณแก้ม แล้วก็มีเลือดซึมๆ"
  └─────┬─────────────────┘
        │
        ├─────────────────────────────┐
        ▼                             ▼
  ┌──────────────┐           ┌──────────────────┐
  │ Pipeline A   │           │ Pipeline B       │
  │ Symptom      │           │ Risk             │
  │ Mapping      │           │ Classification   │
  │              │           │                  │
  │ Free Text    │           │ ข้อมูลแบบฟอร์ม  │
  │ → ChromaDB   │           │ → Rule Engine    │
  │ → 3-Tier     │           │ → ประเมินเสี่ยง  │
  │ → Match/     │           │ → ต่ำ/กลาง/สูง  │
  │   Reject     │           │ → คำแนะนำ        │
  └──────┬───────┘           └────────┬─────────┘
         │                            │
         └──────────┬─────────────────┘
                    │
                    ▼
         ┌─────────────────────────┐
         │ Context Builder         │
         │ (context_builder.py)    │
         │                         │
         │ รวม:                    │
         │ - Patient Profile       │
         │ - Current Symptoms      │
         │ - Risk Assessment       │
         └──────────┬──────────────┘
                    │
                    ▼
          ┌──────────────────────────────────┐
          │ 2. ผู้ป่วยถามคำถามเพิ่มเติม     │
          │    "ผ่าฟันคุดต้องพักฟื้นกี่วัน?" │
          └──────────┬───────────────────────┘
                     │
                     ▼
          ┌────────────────────────────┐
          │ Pipeline C: RAG Q&A       │
          │                            │
          │ Sufficiency Check          │
          │      ↓                     │
          │ Query Rewrite + Decompose │
          │      ↓                     │
          │ Query Expansion (3x)       │
          │      ↓                     │
          │ Hybrid Search (Dense+BM25)│
          │      ↓                     │
          │ Dedup → Rerank → Diversity│
          │      ↓                     │
          │ Sibling Enrichment         │
          │      ↓                     │
          │ Chunk Validation           │
          │      ↓                     │
          │ LLM Answer Generation     │
          └──────────┬─────────────────┘
                     │
                     ▼
          ┌────────────────────────────┐
          │ 3. Final Response          │
          │                            │
          │ คำตอบ (ภาษาพยาบาล)        │
          │ + Source (rule/rag)         │
          │ + Referenced Chunks        │
          │                            │
          │ → ส่งกลับผ่าน LINE OA     │
          └────────────────────────────┘
```

---

> **หมายเหตุ:** รายงานนี้ครอบคลุม Pipeline ทั้งหมดของ Backend เพื่อใช้เป็นเอกสารประกอบการทำรายงาน Senior Project
