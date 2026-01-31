# 📊 Database Metadata – Postoperative Patient Monitoring System

ระบบติดตามอาการผู้ป่วยหลังผ่าตัดผ่าน Line OA  
มี LLM ช่วยประเมินความเสี่ยง + ให้คำแนะนำ + หลังบ้านตรวจสอบได้

---

## 🧑‍⚕️ Table: nurse
เก็บข้อมูลผู้ใช้งานฝั่งพยาบาล / เจ้าหน้าที่

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัสพยาบาล |
| username | varchar | ชื่อสำหรับ login |
| password_hash | varchar | รหัสผ่าน (hash) |
| full_name | varchar | ชื่อ–นามสกุล |
| role | varchar | บทบาท (admin, nurse) |
| created_at | timestamp | วันที่สร้างบัญชี |

---

## 🧑 Table: patient
ข้อมูลผู้ป่วย (1 คน มีหลายเคสได้)

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัสผู้ป่วย |
| hn | int (unique) | รหัสนักศึกษา |
| first_name | varchar | ชื่อ |
| last_name | varchar | นามสกุล |
| email | varchar | อีเมล |
| phone | varchar | เบอร์โทร |
| birth_date | date | วันเกิด |
| gender | varchar | เพศ |
| created_at | timestamp | วันที่สร้าง |

---

## 📁 Table: patient_case
เคสการรักษา (ผ่าตัด 1 รอบ = 1 case)

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัสเคส |
| patient_id | uuid (FK) | อ้างอิง patient |
| nurse_id | uuid (FK) | พยาบาลผู้ดูแล |
| surgery_date | date | วันที่ผ่าตัด |
| note | text | หมายเหตุ |
| created_at | timestamp | วันที่สร้างเคส |

---

## 🦷 Table: procedure_master
รายการหัตถการมาตรฐานของโรงพยาบาล

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัสหัตถการ |
| name | varchar | ชื่อหัตถการ |
| is_standard | boolean | เป็นรายการมาตรฐานหรือไม่ |

---

## 🔗 Table: patient_case_procedure
เชื่อม **เคส ↔ หัตถการ** (รองรับ free text)

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัส |
| case_id | uuid (FK) | อ้างอิง patient_case |
| procedure_id | uuid (FK, nullable) | อ้างอิง procedure_master |
| custom_procedure_text | varchar | หัตถการอื่น ๆ (free text) |

📌 ใช้กรณี:
- เลือกจากรายการ → `procedure_id`
- พิมพ์เอง → `custom_procedure_text`

---

## 💬 Table: line_account
ผูก Line OA กับผู้ป่วย

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัส |
| patient_id | uuid (FK) | ผู้ป่วย |
| line_user_id | varchar | LINE userId |
| linked_at | timestamp | วันที่เชื่อม |

---

## ⏰ Table: follow_schedule
ตารางนัดส่งฟอร์มติดตามอาการ

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัส |
| case_id | uuid (FK) | เคส |
| follow_day_no | int | วันที่ X หลังผ่าตัด |
| follow_date | date | วันที่ส่ง |
| follow_time | time | เวลาส่ง |
| channel | varchar | ช่องทาง (LINE) |
| status | varchar | pending / sent / completed |
| created_at | timestamp | วันที่สร้าง |

---

## 📋 Table: form_template
แม่แบบฟอร์มติดตามอาการ

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัส template |
| name | varchar | ชื่อฟอร์ม |
| version | int | เวอร์ชัน |
| created_at | timestamp | วันที่สร้าง |

---

## 📑 Table: form_section
แบ่ง section ของฟอร์ม  
เช่น Section 1 (พยาบาล), Section 2–3 (ผู้ป่วย)

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัส |
| template_id | uuid (FK) | ฟอร์ม |
| title | varchar | ชื่อ section |
| order_no | int | ลำดับ |

---

## ❓ Table: form_question
คำถามในแต่ละ section

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัสคำถาม |
| section_id | uuid (FK) | Section |
| question_text | text | คำถาม |
| question_type | varchar | text / choice / multi |
| options | json | ตัวเลือก |
| order_no | int | ลำดับ |
| has_extra_note | boolean | มีช่องหมายเหตุหรือไม่ |

---

## 📝 Table: form_submission
การส่งฟอร์ม 1 ครั้ง (1 วัน / 1 schedule)

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัส |
| case_id | uuid (FK) | เคส |
| schedule_id | uuid (FK) | รอบติดตาม |
| template_id | uuid (FK) | ฟอร์ม |
| submitted_at | timestamp | เวลาส่ง |

---

## ✍️ Table: form_answer
คำตอบรายข้อ (normalized)

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัส |
| submission_id | uuid (FK) | การส่งฟอร์ม |
| question_id | uuid (FK) | คำถาม |
| answer_value | text | คำตอบ |
| extra_note | text | หมายเหตุ |

---

## 🤖 Table: llm_risk_evaluation
ผลประเมินความเสี่ยงรายด้านจาก LLM (รอบแรก)

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัส |
| submission_id | uuid (FK) | ฟอร์ม |
| category | varchar | pain / swelling / fever |
| risk_level | varchar | low / medium / high |
| reason | text | เหตุผล |
| recommendation | text | คำแนะนำ |
| model_version | varchar | LLM version |
| created_at | timestamp | เวลาประเมิน |

---

## 🧠 Table: llm_case_summary
LLM รอบที่ 2 สรุปภาพรวม + ข้อความส่งผู้ป่วย

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัส |
| submission_id | uuid (FK) | ฟอร์ม |
| overall_risk | varchar | ความเสี่ยงรวม |
| summary_text | text | สรุปสำหรับ staff |
| patient_message | text | ข้อความส่ง LINE |
| created_at | timestamp | เวลา生成 |

---

## 📤 Table: message_log
บันทึกข้อความที่ส่งออกจริง

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัส |
| case_id | uuid (FK) | เคส |
| schedule_id | uuid (FK) | รอบ |
| channel | varchar | LINE |
| message_type | varchar | form / advice / alert |
| content | text | เนื้อหา |
| sent_at | timestamp | เวลาส่ง |

---

## 📄 Table: report_file
ไฟล์สรุปอาการ (PDF)

| Field | Type | Description |
|-----|-----|------------|
| id | uuid (PK) | รหัส |
| submission_id | uuid (FK) | ฟอร์ม |
| file_url | varchar | ที่อยู่ไฟล์ |
| generated_at | timestamp | เวลาสร้าง |

---

## 🔥 Data Flow (TL;DR)
1. Nurse กรอก **Section 1** → สร้าง `patient_case`
2. ระบบสร้าง `follow_schedule`
3. ผู้ป่วยกรอกฟอร์ม → `form_submission + form_answer`
4. LLM #1 ประเมินรายด้าน → `llm_risk_evaluation`
5. LLM #2 สรุปภาพรวม → `llm_case_summary`
6. ส่ง LINE + เก็บ log + export PDF

---

> โครงนี้ **normalized, audit ได้, อธิบายอาจารย์ได้, scale ต่อได้จริง**
s