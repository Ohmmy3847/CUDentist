# การเปรียบเทียบ Field Names ระหว่าง Frontend และ Backend

## ✅ ตรวจสอบทั้งหมดแล้ว - พบความไม่ตรงกัน 2 จุด!

---

## ⚠️ ปัญหาที่พบ

### 1. **brushing_teeth** - ไม่ตรงกัน!

**Frontend (form.types.ts):**
```typescript
brushing_teeth?: 'แปรงฟันได้' | 'แปรงฟันไม่ได้' | string;
```

**Backend (flow_parser.py):**
```python
brushing = data.get('brushing_teeth', '')

# เช็คเงื่อนไข:
- "แปรงฟันไม่ได้" / "แปรงไม่ได้" / "ไม่ได้แปรง"
- "ไม่ถนัด" / "แปรงไม่ถนัด"  ← Frontend ไม่มีตัวเลือกนี้แต่ Backend รองรับ
- "แปรงได้" / "แปรงฟันได้" / "ได้"
```

**🔥 ปัญหา:** Frontend มีแค่ 2 ตัวเลือก (แปรงได้, แปรงไม่ได้) แต่ Backend ต้องการ "แปรงฟันไม่ถนัด"

**💡 แนะนำ:** เพิ่มตัวเลือก "แปรงฟันไม่ถนัด" ใน Frontend

---

## ✅ Field Names ที่ถูกต้องแล้ว

| Field Name | Frontend | Backend | สถานะ |
|------------|----------|---------|-------|
| pain_score | ✅ | ✅ | OK |
| pain_medication_effect | ✅ | ✅ | OK |
| swelling_status | ✅ | ✅ | OK |
| breathing_or_swallowing_difficulty | ✅ | ✅ | OK |
| bleeding_status | ✅ | ✅ | OK |
| fever_status | ✅ | ✅ | OK |
| numbness_status | ✅ | ✅ | OK |
| phlebitis | ✅ | ✅ | OK |
| suture_status | ✅ | ✅ | OK |
| other_symptoms | ✅ | ✅ | OK |
| other_symptoms_custom | ✅ | ✅ | OK |
| antibiotic_compliance | ✅ | ✅ | OK |
| compress_type | ✅ | ✅ | OK |
| has_imf | ✅ | ✅ | OK |
| imf_wire_status | ✅ | ✅ | OK |
| walking_status | ✅ | ✅ | OK |
| brushing_teeth | ⚠️ | ⚠️ | **ต้องเพิ่มตัวเลือก** |
| mouth_rinsing | ✅ | ✅ | OK |
| feeding_method | ✅ | ✅ | OK |
| food_types | ✅ | ✅ | OK |
| food_amount | ✅ | ✅ | OK |
| ng_tube_position | ✅ | ✅ | OK |
| procedures | ✅ | ✅ | OK |

---

## 📋 รายละเอียดเปรียบเทียบแต่ละ Field

### 1. pain_score ✅
- Frontend: `pain_score?: number;`
- Backend: `data.get('pain_score')`
- **สถานะ:** OK

### 2. pain_medication_effect ✅
- Frontend: `pain_medication_effect?: 'ดีขึ้น' | 'ไม่ดีขึ้น' | 'ไม่ได้ทานยาแก้ปวด'`
- Backend: `data.get('pain_medication_effect', '')`
- **สถานะ:** OK

### 3. swelling_status ✅
- Frontend: `swelling_status?: 'ปัจจุบันหายบวมแล้ว' | 'บวมลดลง' | 'บวมเท่าเดิม' | 'บวมมากขึ้น' | ...`
- Backend: `data.get('swelling_status', '')`
- **สถานะ:** OK

### 4. breathing_or_swallowing_difficulty ✅
- Frontend: `breathing_or_swallowing_difficulty?: 'ไม่มี' | 'มี' | string`
- Backend: `data.get('breathing_or_swallowing_difficulty', '')`
- **สถานะ:** OK

### 5. bleeding_status ✅
- Frontend: `bleeding_status?: 'ไม่มีเลือดซึมหรือไหลแล้ว' | 'เลือดซึม แต่หยุดได้เอง' | ...`
- Backend: `data.get('bleeding_status', '')`
- **สถานะ:** OK

### 6. fever_status ✅
- Frontend: `fever_status?: 'ไม่มีไข้' | 'มีไข้ (มากกว่า 38 องศาเซลเซียส)' | string`
- Backend: `data.get('fever_status', '')`
- **สถานะ:** OK

### 7. numbness_status ✅
- Frontend: `numbness_status?: 'หายชาแล้วหลังทำหัตถการ' | 'ยังชาอยู่แต่ชาน้อยลงเรื่อยๆ' | ...`
- Backend: `data.get('numbness_status', '')`
- **สถานะ:** OK

### 8. phlebitis ✅
- Frontend: `phlebitis?: 'ไม่มีอาการปวด/บวม/แดง รอบรอยเข็ม' | 'มีอาการปวด/บวม/แดง รอบรอยเข็ม'`
- Backend: `data.get('phlebitis', '')`
- **สถานะ:** OK

### 9. suture_status ✅
- Frontend: `suture_status?: 'ไหมแน่นดี / ไม่ได้สังเกต' | 'ไหมหลุดหายไปบางส่วน แต่ไม่มีเลือดไหล' | ...`
- Backend: `data.get('suture_status', '')`
- **สถานะ:** OK

### 10. other_symptoms + other_symptoms_custom ✅
- Frontend: `other_symptoms?: string[]` + `other_symptoms_custom?: string[]`
- Backend: `data.get('other_symptoms', [])` + `data.get('other_symptoms_custom', '')`
- **สถานะ:** OK

### 11. antibiotic_compliance ✅
- Frontend: `antibiotic_compliance?: 'ครบตามแพทย์สั่ง' | 'ลืมทานบางครั้ง' | 'ไม่ได้ทานเลย'`
- Backend: `data.get('antibiotic_compliance', '')`
- **สถานะ:** OK

### 12. compress_type ✅
- Frontend: `compress_type?: 'ประคบเย็นอยู่' | 'ประคบอุ่นอยู่' | 'ไม่ได้ประคบอะไรเลย'`
- Backend: `data.get('compress_type', '')`
- **สถานะ:** OK

### 13. has_imf + imf_wire_status ✅
- Frontend: `has_imf?: 'มีการมัดฟัน' | 'ไม่มีการมัดฟัน'`
- Frontend: `imf_wire_status?: 'ลวด/ยางมัดฟันแน่นดี' | ...`
- Backend: `data.get('has_imf', '')` + `data.get('imf_wire_status', '')`
- **สถานะ:** OK

### 14. walking_status ✅
- Frontend: `walking_status?: 'ไม่ได้ทำหัตถการ...' | 'เดินได้ปกติ' | 'เดินไม่ถนัด'`
- Backend: `data.get('walking_status', '')`
- **สถานะ:** OK

### 15. brushing_teeth ⚠️ **ต้องแก้ไข!**
- Frontend: `brushing_teeth?: 'แปรงฟันได้' | 'แปรงฟันไม่ได้' | string`
- Backend: รองรับ "แปรงฟันไม่ถนัด" แต่ Frontend ไม่มี
- **ปัญหา:** Frontend ขาดตัวเลือก "แปรงฟันไม่ถนัด"

### 16. mouth_rinsing ✅
- Frontend: `mouth_rinsing?: 'บ้วนปากได้' | 'บ้วนปากไม่ได้'`
- Backend: `data.get('mouth_rinsing', '')`
- **สถานะ:** OK

### 17. feeding_method ✅
- Frontend: `feeding_method?: 'รับประทานอาหารผ่านกระบอกฉีดยา (syringe)' | ...`
- Backend: `data.get('feeding_method', '')`
- **สถานะ:** OK

### 18. food_types ✅
- Frontend: `food_types?: string[]`
- Backend: `data.get('food_types', [])`
- **สถานะ:** OK

### 19. food_amount ✅
- Frontend: `food_amount?: 'รับประทานอาหารปริมาณปกติ' | 'รับประทานอาหารได้น้อยลง'`
- Backend: `data.get('food_amount', '')`
- **สถานะ:** OK

### 20. ng_tube_position ✅
- Frontend: `ng_tube_position?: 'สายยางอยู่ในตำแหน่งเดิม...' | 'สายยางเลื่อนตำแหน่ง...'`
- Backend: `data.get('ng_tube_position', '')`
- **สถานะ:** OK

---

## 🎯 สรุปและแนะนำ

### ปัญหาที่ต้องแก้

**1. Frontend: เพิ่มตัวเลือก "แปรงฟันไม่ถนัด" ใน DailyLifeForm.tsx**

ตอนนี้ Frontend มีแค่:
- แปรงฟันได้
- แปรงฟันไม่ได้ (แต่นี่คือไม่ได้แปรงเลย)

ควรเพิ่ม:
- **แปรงฟันไม่ถนัด** (แปรงได้แต่ลำบาก)

เพราะ Backend รองรับแล้วและมันคนละความหมายกับ "แปรงฟันไม่ได้"

---

## ✅ สรุป
- **Field names ตรงกันหมดแล้ว** 
- **ตัวเลือกส่วนใหญ่ตรงกัน**
- **ต้องเพิ่มตัวเลือก "แปรงฟันไม่ถนัด" ใน Frontend เท่านั้น**
