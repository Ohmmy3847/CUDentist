# Setup Guide - DeepSeek API

## เปลี่ยนจาก Gemini มาใช้ DeepSeek แล้ว! 🚀

### 1. สมัคร DeepSeek API Key

1. ไปที่ https://platform.deepseek.com/
2. สมัครบัญชี
3. สร้าง API key
4. คัดลอก API key

### 2. ตั้งค่า Environment Variable

เพิ่ม `DEEPSEEK_API_KEY` ในไฟล์ `backend/.env`:

```bash
# DeepSeek API (for evaluation)
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. ติดตั้ง Dependencies

```bash
cd backend
pip install langchain-openai deepeval
```

### 4. ทดสอบ

```bash
cd evaluation
python -c "import os; os.environ['DEEPSEEK_API_KEY']='test'; from langchain_openai import ChatOpenAI; print('✅ Ready!')"
```

### 5. รัน Evaluation

```bash
# ใช้ launcher
python launcher.py

# หรือรันตรง
cd summary_evaluation
python scripts/quick_eval_th.py
```

## ข้อดีของ DeepSeek

- ✅ **ราคาถูกกว่า** Gemini และ GPT-4
- ✅ **ประสิทธิภาพดี** สำหรับภาษาไทย
- ✅ **API เสถียร** และรวดเร็ว
- ✅ **Context window ใหญ่** รองรับ evaluation ที่ซับซ้อน

## ราคา (เดือน ก.พ. 2026)

- Input: $0.14 / 1M tokens
- Output: $0.28 / 1M tokens
- Cache hit: $0.014 / 1M tokens

(ถูกกว่า Gemini และ GPT-4 มาก!)

## การเปลี่ยนแปลง

### Metrics ที่อัปเดต
- ✅ `conciseness.py` - ใช้ DeepSeek
- ✅ `completeness.py` - ใช้ DeepSeek
- ✅ `helpfulness.py` - ใช้ DeepSeek
- ⚠️ `faithfulness.py` - ยังใช้ DeepEval (ไม่เปลี่ยน)

### Configuration Files
- ✅ `quick_eval_th.py` - ใช้ DEEPSEEK_API_KEY
- ✅ `quick_eval_en.py` - ใช้ DEEPSEEK_API_KEY
- ✅ `evaluate_summary.py` - model="deepseek-chat"
- ✅ `README.md` - อัปเดตทุกที่

## Troubleshooting

### Error: "DEEPSEEK_API_KEY not found"
```bash
# ตรวจสอบว่ามี API key ใน .env
cat backend/.env | grep DEEPSEEK_API_KEY
```

### Error: "No module named 'langchain_openai'"
```bash
pip install langchain-openai
```

### Error: "No module named 'deepeval'"
```bash
pip install deepeval
```

## Migration จาก Gemini

ถ้าเคยใช้ Gemini อยู่:
1. ✅ Criteria files ยังใช้ได้ (ไม่ต้องเปลี่ยน)
2. ✅ Test cases ยังใช้ได้ (ไม่ต้องเปลี่ยน)
3. ✅ Results format เหมือนเดิม
4. ⚠️ แค่เปลี่ยน API key จาก GOOGLE_API_KEY → DEEPSEEK_API_KEY

## ข้อควรระวัง

- DeepSeek API endpoint: `https://api.deepseek.com`
- Model name: `deepseek-chat`
- Rate limit: ตรวจสอบใน dashboard
- Cost tracking: ดูได้ที่ platform.deepseek.com
