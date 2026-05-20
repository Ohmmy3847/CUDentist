# 🧪 Experiment Plan — CU Dentist Pipeline Evaluation

> **เป้าหมาย:** ทดสอบและหาเหตุผลสนับสนุนทุก Design Decision ในระบบ เพื่อตอบ "ทำไมถึงเลือกค่า/โมเดลนี้" ได้ทุกจุด

---

## สรุปภาพรวม: ทั้งหมด 7 Experiments

| # | Experiment | สิ่งที่ทดสอบ | Pipeline |
|---|---|---|---|
| 1 | Embedding Model Selection | เปรียบเทียบ 3 Embedding Models | ทั้ง Symptom + RAG |
| 2 | LLM Model Selection | เปรียบเทียบ 3 LLM Models | RAG + Symptom + Risk Summary |
| 3 | Chunking Strategy | เปรียบเทียบ Chunk Size + Technique | RAG |
| 4 | Retrieval Parameters | หาค่า K, Expansion, Diversity ที่ดีที่สุด | RAG |
| 5 | Symptom Mapping Thresholds | หาค่า Threshold ที่ดีที่สุด | Symptom |
| 6 | Hybrid Search Weights | Dense vs BM25 Ratio | RAG |
| 7 | Risk Summary Quality | เปรียบเทียบคุณภาพ LLM สรุปความเสี่ยง | Risk Summary |

---

## 📦 สิ่งที่ต้องเตรียมก่อนเริ่ม (Evaluation Dataset)

### Dataset 1: RAG Evaluation Set (ชุดคำถาม-คำตอบ)

เตรียม **40 คู่คำถาม-คำตอบ** ที่ทันตแพทย์ตรวจสอบแล้ว (Ground Truth)

```
┌───────────────────────────────────────────────────────────────┐
│  RAG Evaluation Dataset (eval_rag.json)                       │
├───────────────────────────────────────────────────────────────┤
│  ── Type A: คำถามทั่วไป (ใช้ RAG อย่างเดียว) ──             │
│  {                                                            │
│    "id": 1,                                                   │
│    "question": "ผ่าฟันคุดต้องพักฟื้นกี่วัน?",               │
│    "patient_context": null,                                    │
│    "ground_truth": "ระยะเวลาพักฟื้น 3-4 วัน ...",           │
│    "relevant_sources": ["047_ผ่าฟันคุด...md"],               │
│    "category": "post_op_care",                                │
│    "question_type": "rag_only"                                │
│  },                                                           │
│                                                               │
│  ── Type B: ต้องรวม Context + RAG ──                         │
│  {                                                            │
│    "id": 25,                                                  │
│    "question": "วันนี้กินอะไรได้บ้าง?",                      │
│    "patient_context": {                                        │
│      "procedures": ["ผ่าตัดขากรรไกร BSSRO"],                 │
│      "days_post_op": 3,                                       │
│      "risk_level": "ปานกลาง"                                 │
│    },                                                         │
│    "ground_truth": "ช่วงสัปดาห์แรกหลังผ่าตัดขากรรไกร        │
│      ควรรับประทานอาหารเหลวใส/อาหารปั่น ...",                 │
│    "relevant_sources": ["009_คำแนะนำ...ขากรรไกร.md"],        │
│    "category": "diet",                                        │
│    "question_type": "context_rag_fusion"                      │
│  },                                                           │
│                                                               │
│  ── Type C: Context เพียงพอ (ไม่ต้องค้น RAG) ──              │
│  {                                                            │
│    "id": 35,                                                  │
│    "question": "ผลประเมินความเสี่ยงของผมเป็นยังไง?",        │
│    "patient_context": {                                        │
│      "risk_level": "สูง",                                     │
│      "recommendations": ["ติดต่อแพทย์ทันที"]                 │
│    },                                                         │
│    "ground_truth": "ผลประเมินพบความเสี่ยงสูง ...",           │
│    "relevant_sources": [],                                     │
│    "category": "risk_info",                                   │
│    "question_type": "context_sufficient"                      │
│  }                                                            │
└───────────────────────────────────────────────────────────────┘
```

**แบ่งตามประเภทคำถาม (40 ข้อ):**

| Type | จำนวน | คำอธิบาย | ทดสอบอะไร |
|---|---|---|---|
| **A: RAG Only** | 20 ข้อ | คำถามทั่วไป ไม่ต้องใช้ Context ผู้ป่วย | Retrieval + Generation ปกติ |
| **B: Context+RAG Fusion** | 10 ข้อ | ต้องใช้ข้อมูลผู้ป่วย (หัตถการ, วันหลังผ่าตัด) ร่วมกับ RAG เพื่อตอบให้ตรงสถานการณ์ | Context Builder + คำตอบเฉพาะบุคคล |
| **C: Context Sufficient** | 5 ข้อ | ตอบได้จาก Risk Assessment + Context อย่างเดียว ไม่ต้องค้น RAG | Sufficiency Check ใน pipeline.py |
| **D: Multi-procedure** | 5 ข้อ | ผู้ป่วยทำหลายหัตถการ ต้องยึด Most Restrictive Wins | Context + RAG + กฎ Most Restrictive |

**ตัวอย่างคำถาม Type B (Context + RAG):**
- "วันนี้กินอะไรได้บ้าง?" + context: ผ่าตัดขากรรไกร วันที่ 3 → ต้องตอบ "อาหารเหลวปั่น" (ไม่ใช่อาหารทั่วไป)
- "ออกกำลังกายได้แล้วหรือยัง?" + context: ผ่าตัดขากรรไกร วันที่ 10 → ต้องตอบ "ยังไม่ได้ ต้องรอสัปดาห์ที่ 12"
- "แปรงฟันได้เลยไหม?" + context: ผ่าฟันคุด วันที่ 1 → ต้องตอบ "ยังไม่ควรแปรง ใช้น้ำเกลืออุ่นบ้วนแทน"

**ตัวอย่างคำถาม Type D (Multi-procedure):**
- "กินอะไรได้บ้าง?" + context: ผ่าตัดขากรรไกร + ถอนฟัน → ต้องยึดข้อจำกัดของขากรรไกร (อาหารเหลวปั่น ไม่ใช่อาหารอ่อน)

**วิธีสร้าง:**
1. เลือกคำถามที่ผู้ป่วยถามบ่อย (ครอบคลุมหลากหลายหัตถการ)
2. ให้ทันตแพทย์เขียน Ground Truth Answer (คำตอบที่ถูกต้อง)
3. ระบุ Relevant Source Documents (ไฟล์ที่ควรถูกดึงมา)
4. แบ่ง Category: post_op_care, medication, emergency, diet, hygiene, exercise, risk_info

### Dataset 2: Symptom Mapping Evaluation Set

เตรียม **50–80 คู่อาการ** ที่มี Ground Truth Label

```
┌───────────────────────────────────────────────────────────────┐
│  Symptom Evaluation Dataset (eval_symptom.json)               │
├───────────────────────────────────────────────────────────────┤
│  {                                                            │
│    "id": 1,                                                   │
│    "input": "ปากแห้งมากเลยค่ะ",                              │
│    "expected_symptom": "ปากแห้ง",                             │
│    "should_match": true,                                      │
│    "difficulty": "easy"                                       │
│  },                                                           │
│  {                                                            │
│    "id": 2,                                                   │
│    "input": "รู้สึกชาที่ริมฝีปากล่าง",                       │
│    "expected_symptom": "ชาบริเวณริมฝีปาก",                   │
│    "should_match": true,                                      │
│    "difficulty": "medium"                                     │
│  },                                                           │
│  {                                                            │
│    "id": 3,                                                   │
│    "input": "อยากกินส้มตำ",                                  │
│    "expected_symptom": null,                                   │
│    "should_match": false,                                     │
│    "difficulty": "negative"                                   │
│  }                                                            │
└───────────────────────────────────────────────────────────────┘
```

**วิธีสร้าง:**
1. **Easy (20 ข้อ):** พิมพ์ตรงๆ เช่น "ปากแห้ง" → ปากแห้ง
2. **Medium (20 ข้อ):** พูดอ้อมๆ เช่น "รู้สึกชาตรงริมฝีปาก" → ชาบริเวณริมฝีปาก
3. **Hard (10 ข้อ):** ภาษาชาวบ้าน/สแลง เช่น "คอหัก" → คอแข็ง/ขากรรไกรค้าง
4. **Negative (10 ข้อ):** ไม่ใช่อาการ เช่น "อยากกินส้มตำ" → ไม่ควร Match

### Dataset 3: Risk Summary Evaluation Set

เตรียม **20–25 Scenarios** ของผู้ป่วยที่มี Risk Profile ต่างกัน

```
┌───────────────────────────────────────────────────────────────┐
│  Risk Summary Evaluation Dataset (eval_risk_summary.json)     │
├───────────────────────────────────────────────────────────────┤
│  {                                                            │
│    "id": 1,                                                   │
│    "patient_name": "สมชาย",                                  │
│    "overall_risk": "High",                                    │
│    "risk_results": {                                          │
│      "pain": {"risk_level": "สูง", "reason": "ปวดมาก 9/10"},│
│      "bleeding": {"risk_level": "ปานกลาง", ...}              │
│    },                                                         │
│    "expected_summary_keywords": ["ปวดมาก","เลือด"],          │
│    "expected_urgency": "เร่งด่วน",                            │
│    "category": "high_risk"                                    │
│  },                                                           │
│  {                                                            │
│    "id": 15,                                                  │
│    "patient_name": "สมหญิง",                                 │
│    "overall_risk": "Complicated",                             │
│    "unmapped_symptoms": ["น้ำเหลืองไหลจากจมูก","หูอื้อ"],   │
│    "risk_results": { ... },                                   │
│    "expected_summary_keywords": ["ซับซ้อน","ปรึกษาแพทย์"],   │
│    "expected_urgency": "ซับซ้อน",                             │
│    "category": "complicated"                                  │
│  }                                                            │
└───────────────────────────────────────────────────────────────┘
```

**วิธีสร้าง:**
1. **High Risk (5 ข้อ):** สถานการณ์เสี่ยงสูง (ปวดมาก, เลือดไม่หยุด, ฯลฯ)
2. **Medium Risk (5 ข้อ):** สถานการณ์เสี่ยงปานกลาง (บวมเยอะ, ไข้ต่ำ)
3. **Low Risk (5 ข้อ):** สถานการณ์ปกติ (ไม่ใช้ LLM แต่เทสว่า format ถูก)
4. **Complicated Risk (5 ข้อ):** อาการที่ Symptom Mapping จับคู่ไม่ได้ (เช่น น้ำเหลืองไหลจากจมูก, หูอื้อ, ผื่นขึ้น) → ระบบต้องระบุเป็น "ซับซ้อน" และแนะนำให้ปรึกษาแพทย์
5. **Mixed Risk (5 ข้อ):** หลาย Flows ผสม (High + Medium + Low + Complicated)

### Evaluation Metrics ที่จะใช้

```
┌──────────────────────────────────────────────────────────────────────┐
│                      Evaluation Metrics                              │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  📊 Retrieval-based (วัดคุณภาพการดึงข้อมูล)                         │
│  ├── Precision@K     : สัดส่วน chunks ที่ดึงมาได้ที่เกี่ยวข้องจริง │
│  ├── Recall@K        : สัดส่วน chunks สำคัญที่ถูกดึงมาได้          │
│  ├── MRR             : ตำแหน่งเฉลี่ยของ chunk ที่ถูกต้องตัวแรก     │
│  └── nDCG            : คุณภาพการจัดอันดับ (ยิ่งตัวสำคัญอยู่บนยิ่งดี)│
│                                                                      │
│  📝 Generation-based (วัดคุณภาพคำตอบ)                               │
│  ├── BERTScore       : ความหมายใกล้เคียง Ground Truth               │
│  ├── ROUGE-L         : ลำดับคำที่ตรงกับ Ground Truth                │
│  └── BLEU            : ความแม่นยำระดับคำ/วลี                        │
│                                                                      │
│  👨‍⚕️ Human Evaluation (ทันตแพทย์ให้คะแนน 1-5)                      │
│  ├── Correctness     : ความถูกต้องทางการแพทย์                       │
│  ├── Relevance       : ความเกี่ยวข้องกับคำถาม                       │
│  └── Helpfulness     : ความเป็นประโยชน์ต่อผู้ป่วย                   │
│                                                                      │
│  🏥 Symptom-specific (วัดคุณภาพจับคู่อาการ)                         │
│  ├── Accuracy        : สัดส่วนที่จับคู่ถูก                          │
│  ├── Precision       : จับคู่แล้วถูกจริงกี่%                        │
│  ├── Recall          : อาการจริงถูกจับคู่ได้กี่%                     │
│  └── F1-Score        : ค่าเฉลี่ยฮาร์โมนิกของ Precision+Recall      │
│                                                                      │
│  🤖 LLM-as-a-Judge (ใช้ GPT-4o ให้คะแนน 1-5)                       │
│  ├── Faithfulness    : คำตอบอ้างอิงจาก Context จริงหรือไม่           │
│  ├── Completeness    : ครอบคลุมข้อมูลสำคัญครบหรือไม่                │
│  └── Relevance       : ตอบตรงคำถามหรือไม่                           │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🧪 Experiment 1: Embedding Model Selection

### วัตถุประสงค์
หาเหตุผลว่าทำไมเลือก `multilingual-e5-large` เป็น Embedding Model

### Candidate Models

| Model | Dimension | ผู้พัฒนา | เหตุผลที่เลือกเป็น Candidate |
|---|---|---|---|
| `intfloat/multilingual-e5-large` | 1024 | Microsoft | ✅ ตัวปัจจุบัน, รองรับภาษาไทย, อันดับสูงใน MTEB |
| `BAAI/bge-m3` | 1024 | BAAI | คู่แข่งอันดับต้นใน MTEB, รองรับ multilingual |
| `Alibaba/gte-Qwen2-1.5B-instruct` | 1536 | Alibaba | State-of-art ใหม่ล่าสุด, dimension สูงกว่า |

### วิธีทดสอบ

```
┌────────────────────────────────────────────────────────────┐
│  Experiment 1: Embedding Model                              │
│  ตรึง: LLM = DeepSeek, Chunk = Recursive 1500 chars       │
│  เปลี่ยน: Embedding Model (3 ตัว)                         │
└────────────────────────────────────────────────────────────┘

  สำหรับแต่ละ Embedding Model:
  1. Re-ingest เอกสารทั้งหมด (สร้าง Vector DB ใหม่)
  2. Re-ingest Symptom CSV (สร้าง Symptom DB ใหม่)
  3. รัน RAG eval set → วัด Retrieval metrics (Precision, Recall, MRR, nDCG)
  4. รัน Symptom eval set → วัด Accuracy, F1
  5. วัดเวลา + ต้นทุน API
```

### สิ่งที่จะได้

| เปรียบเทียบ | multilingual-e5-large | bge-m3 | gte-Qwen2 |
|---|---|---|---|
| Retrieval Precision@15 | ? | ? | ? |
| Retrieval Recall@15 | ? | ? | ? |
| MRR | ? | ? | ? |
| Symptom Accuracy | ? | ? | ? |
| Symptom F1 | ? | ? | ? |
| Embed Speed (sec/1000 texts) | ? | ? | ? |
| Dimension | 1024 | 1024 | 1536 |
| API Cost | ? | ? | ? |

### คำตอบที่คาดหวัง
> "เลือก multilingual-e5-large เพราะ Retrieval Precision สูงที่สุดที่ X%, รองรับภาษาไทยได้ดี, ต้นทุน API ต่ำกว่า, และ Dimension 1024 ทำให้ DB ขนาดเล็กกว่า gte-Qwen2 (1536)"

---

## 🧪 Experiment 2: LLM Model Selection

### วัตถุประสงค์
หาเหตุผลว่าทำไมเลือก DeepSeek เป็น LLM หลัก

### Candidate Models

| Model | Provider | ข้อดี |
|---|---|---|
| `deepseek-chat` (DeepSeek-V3) | DeepSeek API | ✅ ตัวปัจจุบัน, ราคาถูก, เร็ว |
| `meta-llama/Llama-3.3-70B-Instruct` | OpenRouter | Open-source อันดับ 1, ภาษาไทยพอใช้ |
| `google/gemini-2.0-flash` | Google AI | เร็วมาก, ภาษาไทยดี, ราคาถูก |

### วิธีทดสอบ

```
┌────────────────────────────────────────────────────────────┐
│  Experiment 2: LLM Model                                    │
│  ตรึง: Embedding = e5-large, Chunk = Recursive 1500       │
│  เปลี่ยน: LLM Model (3 ตัว)                               │
└────────────────────────────────────────────────────────────┘

  สำหรับแต่ละ LLM:
  1. ใช้ Vector DB เดิม (ไม่ต้อง Re-ingest)
  2. รัน RAG eval set → วัด Generation metrics (BERTScore, ROUGE-L)
  3. รัน RAG eval set → วัด LLM-as-a-Judge (Faithfulness, Completeness)
  4. รัน Symptom eval set → วัด Arbitration Accuracy (Tier 2)
  5. รัน Risk Summary eval set → วัดคุณภาพการสรุปความเสี่ยง
  6. วัดเวลาตอบ + ต้นทุน API
```

### สิ่งที่จะได้

| เปรียบเทียบ | DeepSeek-V3 | Llama-3.3-70B | Gemini-2.0-flash |
|---|---|---|---|
| BERTScore | ? | ? | ? |
| ROUGE-L | ? | ? | ? |
| Faithfulness (1-5) | ? | ? | ? |
| Completeness (1-5) | ? | ? | ? |
| Symptom Arbitration Acc | ? | ? | ? |
| Risk Summary Quality (1-5) | ? | ? | ? |
| Risk Summary Faithfulness (1-5) | ? | ? | ? |
| Avg Response Time (sec) | ? | ? | ? |
| Cost per 1K tokens | ? | ? | ? |

### คำตอบที่คาดหวัง
> "เลือก DeepSeek-V3 เพราะ BERTScore ใกล้เคียง Llama-3.3-70B แต่ราคาถูกกว่า 5 เท่า, Faithfulness สูงสุดที่ X/5, Risk Summary สรุปเหตุผลได้กระชับตรงประเด็น, และตอบคำถามภาษาไทยได้ถูกต้องตามบริบททันตกรรม"

---

## 🧪 Experiment 3: Chunking Strategy

### วัตถุประสงค์
หาเหตุผลว่าทำไมใช้ Recursive Chunking ขนาด 1500 chars + overlap 200

### Conditions ที่ทดสอบ

| Config | Technique | Max Chars | Overlap |
|---|---|---|---|
| A | Recursive (Section-Aware) | 1000 | 150 |
| B | Recursive (Section-Aware) | 1500 | 200 |
| C | Recursive (Section-Aware) | 2500 | 300 |
| D | Fixed Character Split | 1500 | 200 |

### วิธีทดสอบ

```
┌────────────────────────────────────────────────────────────┐
│  Experiment 3: Chunking Strategy                            │
│  ตรึง: LLM = DeepSeek, Embedding = e5-large               │
│  เปลี่ยน: Chunk Size + Technique (4 configs)              │
└────────────────────────────────────────────────────────────┘

  สำหรับแต่ละ Config:
  1. Re-ingest เอกสารทั้งหมด (ด้วย Chunk config ที่ต่างกัน)
  2. บันทึกจำนวน Chunks ที่ได้ + ขนาดเฉลี่ย
  3. รัน RAG eval set → วัด Retrieval + Generation metrics
  4. วัดเวลา Ingestion + ขนาด DB
```

### สิ่งที่จะได้

| เปรียบเทียบ | A (1000) | B (1500) ✅ | C (2500) | D (Fixed) |
|---|---|---|---|---|
| จำนวน Chunks | ? | 2206 | ? | ? |
| Avg Chunk Size (chars) | ? | ? | ? | ? |
| Precision@15 | ? | ? | ? | ? |
| Recall@15 | ? | ? | ? | ? |
| BERTScore (Answer) | ? | ? | ? | ? |
| Completeness (1-5) | ? | ? | ? | ? |

### คำตอบที่คาดหวัง
> "เลือก Recursive 1500 chars เพราะ Chunk ใหญ่พอที่จะเก็บบริบทครบ (ไม่ตัดกลางประโยค) แต่ไม่ใหญ่เกินจนทำให้ Precision ตก, Section-Aware ทำให้ Recall สูงกว่า Fixed Split เพราะไม่หั่นข้ามหัวข้อ"

---

## 🧪 Experiment 4: Retrieval Parameters (RAG Tunables)

### วัตถุประสงค์
หาเหตุผลว่าทำไมค่า INITIAL_K=30, RERANK_TOP_K=15, NUM_EXPANSIONS=3 ฯลฯ

### Parameter Sweep

```
┌────────────────────────────────────────────────────────────┐
│  Experiment 4: Retrieval Parameter Sweep                    │
│  ตรึง: LLM, Embedding, Chunk (ค่าที่ดีที่สุดจาก Exp 1-3) │
│  เปลี่ยน: ค่า Retrieval Parameters ทีละตัว                │
└────────────────────────────────────────────────────────────┘
```

### 4A: INITIAL_K (จำนวน docs ที่ดึงต่อ query)

| ค่าที่ทดสอบ | 10 | 20 | **30** ✅ | 50 |
|---|---|---|---|---|
| Recall@K | ? | ? | ? | ? |
| Precision@K | ? | ? | ? | ? |
| Response Time (sec) | ? | ? | ? | ? |

### 4B: RERANK_TOP_K (จำนวนที่เก็บหลัง Rerank)

| ค่าที่ทดสอบ | 5 | 10 | **15** ✅ | 20 |
|---|---|---|---|---|
| Completeness (1-5) | ? | ? | ? | ? |
| Faithfulness (1-5) | ? | ? | ? | ? |
| Response Time (sec) | ? | ? | ? | ? |

### 4C: NUM_EXPANSIONS (จำนวน Expanded Queries)

| ค่าที่ทดสอบ | 1 | 2 | **3** ✅ | 5 |
|---|---|---|---|---|
| Recall@K | ? | ? | ? | ? |
| Response Time (sec) | ? | ? | ? | ? |

### 4D: Sibling Enrichment (ON vs OFF)

| ค่าที่ทดสอบ | OFF | **ON (Top 3 sources, max 10)** ✅ |
|---|---|---|
| Completeness (1-5) | ? | ? |
| BERTScore | ? | ? |

### คำตอบที่คาดหวัง
> "INITIAL_K=30 เป็นจุด Sweet Spot: Recall สูงถึง X% โดย Response Time เพิ่มจาก K=20 แค่ Y วินาที แต่ถ้าเพิ่มเป็น 50 Time เพิ่มขึ้น Z% โดย Recall เพิ่มแค่ 1-2%"

---

## 🧪 Experiment 5: Symptom Mapping Thresholds

### วัตถุประสงค์
หาเหตุผลว่าทำไม AUTO_ACCEPT=0.90, LLM_THRESHOLD=0.70

### Threshold Sweep

```
┌────────────────────────────────────────────────────────────┐
│  Experiment 5: Symptom Threshold Sweep                      │
│  ตรึง: Embedding = e5-large, LLM = DeepSeek               │
│  เปลี่ยน: Threshold values                                │
└────────────────────────────────────────────────────────────┘

  ใช้ Symptom eval set (50-80 คู่) รันผ่าน Pipeline
  โดยเปลี่ยน Threshold ทีละค่า แล้ววัดผล
```

### 5A: AUTO_ACCEPT_THRESHOLD

| ค่า | 0.85 | 0.88 | **0.90** ✅ | 0.93 | 0.95 |
|---|---|---|---|---|---|
| Auto Accept Rate | ? | ? | ? | ? | ? |
| False Positive Rate | ? | ? | ? | ? | ? |
| Accuracy | ? | ? | ? | ? | ? |
| LLM Calls Saved | ? | ? | ? | ? | ? |

### 5B: LLM_THRESHOLD (ขอบล่างก่อน Reject)

| ค่า | 0.60 | 0.65 | **0.70** ✅ | 0.75 | 0.80 |
|---|---|---|---|---|---|
| Rejection Rate | ? | ? | ? | ? | ? |
| False Negative Rate | ? | ? | ? | ? | ? |
| Accuracy | ? | ? | ? | ? | ? |
| LLM Calls Needed | ? | ? | ? | ? | ? |

### คำตอบที่คาดหวัง
> "AUTO_ACCEPT=0.90: ที่ค่านี้ False Positive เป็น 0% (ไม่เคยจับคู่ผิด) และสามารถข้าม LLM call ได้ X% ของ queries, ถ้าลดเป็น 0.85 จะเริ่มมี False Positive Y%"
> "LLM_THRESHOLD=0.70: ต่ำกว่านี้ LLM ตัดสินผิดบ่อย เพราะ Candidate ห่างจากอาการจริงเกินไป"

---

## 🧪 Experiment 6: Hybrid Search Weights

### วัตถุประสงค์
หาเหตุผลว่าทำไมใช้ Dense 0.6 / BM25 0.4

### Weight Sweep

| Config | Dense Weight | BM25 Weight |
|---|---|---|
| A | 1.0 | 0.0 (Dense Only) |
| B | 0.8 | 0.2 |
| C | **0.6** ✅ | **0.4** ✅ |
| D | 0.5 | 0.5 |
| E | 0.4 | 0.6 |
| F | 0.0 | 1.0 (BM25 Only) |

### สิ่งที่จะได้

| Config | Precision@15 | Recall@15 | MRR | nDCG |
|---|---|---|---|---|
| Dense Only | ? | ? | ? | ? |
| 0.8/0.2 | ? | ? | ? | ? |
| **0.6/0.4** ✅ | ? | ? | ? | ? |
| 0.5/0.5 | ? | ? | ? | ? |
| 0.4/0.6 | ? | ? | ? | ? |
| BM25 Only | ? | ? | ? | ? |

### คำตอบที่คาดหวัง
> "Dense 0.6 + BM25 0.4 ให้ MRR สูงที่สุดที่ X เพราะ Dense จับ Semantic ได้ดี แต่ BM25 ช่วยดึง Keyword ภาษาไทยที่ Embedding พลาด เช่น ชื่อยา/ชื่อหัตถการเฉพาะ"

---

## 🧪 Experiment 7: Risk Summary Quality

### วัตถุประสงค์
หาเหตุผลว่า LLM สรุปผลประเมินความเสี่ยงได้ดีแค่ไหน และเปรียบเทียบระหว่าง LLM ที่ต่างกัน

### สิ่งที่ LLM ทำใน Risk Pipeline

| Function | LLM ทำอะไร | เมื่อไหร่ |
|---|---|---|
| `_generate_patient_summary()` | สรุปสาเหตุความเสี่ยง (ต่อท้าย "เนื่องจาก...") | High/Medium Risk เท่านั้น |
| `answer_patient_questions()` | ตอบคำถามผู้ป่วยพร้อม urgency + should_contact_doctor | ทุกครั้งที่ถาม |

> Low Risk ไม่ใช้ LLM (ใช้ Rule-based format โดยตรง)

### วิธีทดสอบ

```
┌────────────────────────────────────────────────────────────┐
│  Experiment 7: Risk Summary Quality                         │
│  ทดสอบร่วมกับ Exp 2 (ใช้ LLM 3 ตัวเดียวกัน)              │
│  เปลี่ยน: LLM Model (3 ตัว)                               │
└────────────────────────────────────────────────────────────┘

  สำหรับแต่ละ LLM:
  1. ใช้ Risk Summary eval set (15-20 scenarios)
  2. วัดคุณภาพ Summary:
     - Faithfulness: สรุปตรงกับ Input Risk ที่ให้ไหม
     - Conciseness: กระชับ ไม่ยาวเกิน
     - Accuracy: ไม่แต่งเติมข้อมูลเกิน
  3. วัดคุณภาพ Patient Q&A (จาก summarizer):
     - Urgency correctness: urgency_level ตรงกับ scenario
     - Should_contact_doctor accuracy
```

### สิ่งที่จะได้

| เปรียบเทียบ | DeepSeek-V3 | Llama-3.3-70B | Gemini-2.0-flash |
|---|---|---|---|
| Summary Faithfulness (1-5) | ? | ? | ? |
| Summary Conciseness (1-5) | ? | ? | ? |
| No Hallucination Rate (%) | ? | ? | ? |
| Urgency Classification Acc | ? | ? | ? |
| Contact Doctor Acc | ? | ? | ? |

### คำตอบที่คาดหวัง
> "DeepSeek-V3 สรุปเหตุผลได้กระชับ Faithfulness X/5 ไม่แต่งเติม, Urgency Classification ตรง Y%"

---

## 📐 ลำดับการทำ Experiments

```
  Exp 1: Embedding Model ──→ ได้ Best Embedding
             │
             ▼
  Exp 2+7: LLM Model ─────→ ได้ Best LLM (ทั้ง RAG + Risk Summary)
             │
             ▼
  Exp 3: Chunk Strategy ───→ ได้ Best Chunk Config
             │
             ▼
  Exp 6: Hybrid Weights ───→ ได้ Best Dense/BM25 Ratio
             │
             ▼
  Exp 4: Retrieval Params ─→ ได้ Best K, Expansion, Diversity
             │
             ▼
  Exp 5: Symptom Thresholds → ได้ Best Accept/Reject Thresholds
```

> ⚠️ ทำตามลำดับนี้ เพราะแต่ละ Experiment จะ "ตรึง" ค่าที่ดีที่สุดจาก Experiment ก่อนหน้า
> Exp 7 ทำพร้อม Exp 2 ได้เลย เพราะใช้ LLM 3 ตัวเดียวกัน

---

## 🛠️ Automation Script (แนวทาง)

สร้าง Script ชื่อ `scripts/run_experiments.py` ที่สามารถ:

```python
# Pseudocode
for embedding_model in ["e5-large", "bge-m3", "gte-qwen2"]:
    # 1. Re-ingest with this embedding
    ingest_rag(embedding=embedding_model)
    ingest_symptom(embedding=embedding_model)
    
    # 2. Run RAG eval
    rag_results = evaluate_rag(eval_set, embedding=embedding_model)
    
    # 3. Run Symptom eval
    symptom_results = evaluate_symptom(eval_set, embedding=embedding_model)
    
    # 4. Log results
    log_results(embedding_model, rag_results, symptom_results)
```

---

## 📊 ผลลัพธ์ที่คาดว่าจะนำเสนอในรายงาน

### ตารางสรุป (ตัวอย่าง)

```
┌──────────────────────────────────────────────────────────────┐
│  Table 1: Embedding Model Comparison                         │
│                                                              │
│  Model              │ P@15  │ R@15  │ MRR   │ Sym-F1 │ Cost │
│  ────────────────────┼───────┼───────┼───────┼────────┼──────│
│  multilingual-e5 ✅  │ 0.82  │ 0.91  │ 0.88  │ 0.94   │ $X  │
│  bge-m3             │ 0.79  │ 0.89  │ 0.85  │ 0.92   │ $Y  │
│  gte-Qwen2          │ 0.81  │ 0.90  │ 0.87  │ 0.93   │ $Z  │
└──────────────────────────────────────────────────────────────┘
  * ตัวเลขเป็นตัวอย่าง ต้องรันจริงถึงจะได้ค่าจริง
```

### กราฟที่ควรมี
1. **Bar Chart:** เปรียบเทียบ Metrics ของแต่ละ Model/Config
2. **Line Chart:** Threshold Sweep (แกน X = Threshold, แกน Y = Accuracy/F1)
3. **Heatmap:** Hybrid Weight Sweep (Dense vs BM25 vs Metrics)
4. **Box Plot:** Human Evaluation Scores (Correctness, Relevance, Helpfulness)

---

## ⏱️ Timeline ประมาณ

| สัปดาห์ | งาน |
|---|---|
| 1 | เตรียม Evaluation Datasets (ให้ทันตแพทย์ตรวจ Ground Truth) |
| 1 | เขียน Evaluation Scripts |
| 2 | Exp 1 (Embedding) + Exp 2 (LLM) |
| 3 | Exp 3 (Chunking) + Exp 6 (Hybrid Weights) |
| 3 | Exp 4 (Retrieval Params) + Exp 5 (Symptom Thresholds) |
| 4 | Human Evaluation (ส่งให้ทันตแพทย์ให้คะแนน) |
| 4 | รวบรวมผล + เขียนรายงาน |
