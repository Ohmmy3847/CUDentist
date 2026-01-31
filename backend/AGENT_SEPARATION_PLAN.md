# แยก Agent สำหรับสร้าง Summary

## เหตุผล
แทนที่จะใช้ LLM เดียวสร้างทั้ง nurse summary และ patient summary พร้อมกัน เราจะแยกเป็น 2 agents:

1. **Nurse Summary Agent** - Focus: Medical terminology, clinical analysis
2. **Patient Summary Agent** - Focus: Easy language, actionable recommendations

## การเปลี่ยนแปลง

### สร้าง 2 Functions ใหม่

```python
def _generate_nurse_summary(
    overall_risk, high_risk, medium_risk, low_risk,
    description_context, procedures, llm
) -> str:
    """Generate summary for nurses with medical terminology"""
    
def _generate_patient_summary(
    overall_risk, high_risk, medium_risk, low_risk,
    recommendations_context, procedures, llm  
) -> str:
    """Generate summary for patients with easy language"""
```

### แก้ไข `summarize_all_risks()`

เรียกทั้ง 2 functions แบบ **parallel** (async) เพื่อประหยัดเวลา:

```python
# Run both summaries in parallel
nurse_summary, patient_summary = await asyncio.gather(
    asyncio.to_thread(_generate_nurse_summary, ...),
    asyncio.to_thread(_generate_patient_summary, ...)
)
```

## ข้อดี
- แต่ละ agent มี focus ชัดเจน
- Prompt สั้นลง อ่านง่ายขึ้น
- คุณภาพดีขึ้น (แต่ละ agent ทำงานเดียว)
- ปรับแต่งแยกกันได้

## ข้อเสีย
- ใช้ 2 LLM calls (แต่รันแบบ parallel จึงไม่ช้ามาก)
