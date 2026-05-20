# ระบบประเมินความเสี่ยงผู้ป่วยหลังผ่าตัด
Post-Operative Patient Risk Assessment System

source .venv/bin/activate
## 📁 โครงสร้างโปรเจกต์

```
Senior_Project/
├── risk_service_api/             # FastAPI Backend
│   ├── main.py                   # REST API endpoints
│   ├── app/                      # Application package (routers/services/models)
│   ├── scripts/                  # Utility scripts
│   ├── data/                     # Data + vector DB files
│   ├── logs/                     # Logs output directory
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Docker configuration
│   └── .env.example              # Environment variables template
│
├── frontend/                     # Next.js Frontend
│   ├── app/                      # Next.js App Router
│   │   ├── page.tsx              # Home page (เลือก Form/CSV)
│   │   ├── layout.tsx            # Root layout
│   │   ├── globals.css           # Global styles
│   │   ├── form/                 # Form page (กรอกฟอร์ม 27 ข้อ)
│   │   ├── upload/               # CSV upload page
│   │   └── result/               # Results display page
│   ├── components/               # Reusable components
│   ├── lib/                      # Utilities
│   │   ├── api.ts                # API client
│   │   └── types.ts              # TypeScript types (27 questions)
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   └── tailwind.config.js
│
├── question.txt                  # คำถาม 27 ข้อ (reference)
└── README.md                     # คู่มือนี้
```

## 🚀 การติดตั้งและรัน

### Backend (FastAPI)

```bash
# 1. เข้าโฟลเดอร์ risk_service_api
cd risk_service_api

# 2. สร้าง virtual environment (ถ้ายังไม่มี)
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# หรือ .venv\Scripts\activate  # Windows

# 3. ติดตั้ง dependencies
pip install -r requirements.txt

# 4. ตั้งค่า environment variables
cp .env.example .env
# แก้ไข .env ใส่ GOOGLE_API_KEY

# 5. รัน API server
python main.py
# API จะรันที่ http://localhost:8000/risk_service_api
# ดู API docs ที่ http://localhost:8000/risk_service_api/docs
```

### Frontend (Next.js)

```bash
# 1. เข้าโฟลเดอร์ frontend
cd frontend

# 2. ติดตั้ง dependencies
npm install
# หรือ yarn install

# 3. ตั้งค่า environment variables
cp .env.local.example .env.local
# แก้ไข NEXT_PUBLIC_API_URL ถ้าจำเป็น

# 4. รัน development server
npm run dev
# หรือ yarn dev
# Frontend จะรันที่ http://localhost:3000
```

## 📝 การใช้งาน

### 1. กรอกแบบฟอร์ม
- เข้า http://localhost:3000
- เลือก "กรอกแบบฟอร์ม"
- กรอกข้อมูลผู้ป่วย 27 คำถาม
- รับผลการประเมินความเสี่ยงทันที

### 2. อัปโหลด CSV
- เข้า http://localhost:3000  
- เลือก "อัปโหลด CSV"
- อัปโหลดไฟล์ CSV (รูปแบบตาม data/66.csv)
- ดาวน์โหลดผลลัพธ์เป็น CSV ที่มีคอลัมน์ risk assessment

## 🔌 API Endpoints

### Backend API

**Base URL:** `http://localhost:8000/risk_service_api`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/flows` | รายชื่อ flows ทั้งหมด |
| POST | `/patient-assessment` | ประเมินความเสี่ยงผู้ป่วย (main endpoint) |
| POST | `/log/submission` | บันทึกผลการประเมิน (logging) |

**ตัวอย่างการเรียกใช้:**

```bash
# Assess patient data
curl -X POST http://localhost:8000/risk_service_api/patient-assessment \
  -H "Content-Type: application/json" \
  -d '{
    "basic_info": {
      "first_name": "สมชาย",
      "last_name": "ใจดี",
      "birth_date": "2000-05-15",
      "hn": "HN12345",
      "procedures": ["BSSRO"],
      "surgery_date": "2026-01-09"
    },
    "assessment_data": {
      "pain_score": 5
    },
    "language": "th"
  }'
```

## 📋 คำถามทั้ง 27 ข้อ

ดูรายละเอียดใน [question.txt](question.txt)

1. อายุ
2. เพศ
3. HN
4. หัตถการที่ทำ (multiple)
5. วันที่ผ่าตัด
6. ระดับความปวด (0-10)
7. ยาแก้ปวดมีผลหรือไม่
8. อาการบวม
9. หายใจ/กลืนลำบาก
10. เลือดออก
11. ไข้
12. ชา
13. Phlebitis (รอยเข็ม)
14. ไหมเย็บแผล
15. อาการอื่นๆ (multiple)
16. ทานยาฆ่าเชื้อ
17. ประคบ
18. การมัดฟัน (IMF)
19. ลวดมัดฟัน
20. การเดิน
21. แปรงฟัน
22. บ้วนปาก
23. วิธีรับประทานอาหาร
24. ประเภทอาหาร (multiple)
25. ปริมาณอาหาร
26. คำถามเพิ่มเติม
27. สายยางให้อาหาร (NG tube)

## 🐳 Deploy ด้วย Docker

### Backend

```bash
cd risk_service_api

# Build image
docker build -t risk-api .

# Run container
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key_here \
  risk-api
```

### Deploy Options

#### 1. **Railway** (แนะนำ - ง่ายที่สุด)

**Backend:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy backend
cd risk_service_api
railway init
railway up
```

**Frontend:**
```bash
cd frontend
railway init
railway up
```

#### 2. **Google Cloud Run**

**Backend:**
```bash
cd risk_service_api

# Build and deploy
gcloud run deploy risk-api \
  --source . \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_key
```

**Frontend:**
```bash
cd frontend

# Deploy to Vercel (ฟรี)
npm install -g vercel
vercel --prod
```

#### 3. **Render.com** (ฟรี)

1. Push code ไป GitHub
2. เข้า [render.com](https://render.com)
3. สร้าง Web Service จาก GitHub repo
4. Backend:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Frontend:
   - Build: `npm install && npm run build`
   - Start: `npm start`

## 🎯 Features

✅ **ประเมินความเสี่ยง** - จำแนก 3 ระดับ: ต่ำ, กลาง, สูง  
✅ **คำแนะนำ** - ให้คำแนะนำการดูแลตนเองตามระดับความเสี่ยง  
✅ **Async Processing** - รัน concurrent API calls เร็วขึ้น 5-10 เท่า  
✅ **CSV Batch Processing** - ประมวลผลผู้ป่วยหลายรายพร้อมกัน  
✅ **Modern UI** - Next.js + Tailwind CSS  
✅ **TypeScript** - Type-safe code  
✅ **API Documentation** - Swagger UI auto-generated  

## 🔧 การพัฒนาต่อ

### สร้างหน้าฟอร์มเต็มรูปแบบ

ไฟล์ที่ต้องสร้างต่อ:
- `frontend/app/form/page.tsx` - หน้ากรอกฟอร์ม 27 ข้อ
- `frontend/app/upload/page.tsx` - หน้าอัปโหลด CSV
- `frontend/components/RiskResult.tsx` - แสดงผลความเสี่ยง

### ปรับปรุง Backend

แก้ไข `risk_service_api/main.py` เพื่อ:
- เพิ่ม authentication
- เพิ่ม rate limiting
- Log การใช้งาน
- Cache ผลลัพธ์

## 📦 Dependencies

### Backend
- FastAPI - Web framework
- Uvicorn - ASGI server
- LangChain - LLM integration
- Google Generative AI - Gemini API
- Pandas - Data processing

### Frontend
- Next.js 14 - React framework
- Tailwind CSS - Styling
- Axios - HTTP client
- React Hook Form - Form management
- Lucide React - Icons

## 🤝 Contributing

1. Fork โปรเจกต์
2. สร้าง feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit การเปลี่ยนแปลง (`git commit -m 'Add AmazingFeature'`)
4. Push ไปยัง branch (`git push origin feature/AmazingFeature`)
5. เปิด Pull Request

## 📄 License

This project is for educational purposes.

## 👥 Authors

Senior Project Team

## 🐛 Known Issues

- ฟอร์ม 27 ข้อยังไม่ได้สร้าง (ต้องสร้างเพิ่ม)
- CSV upload page ยังไม่ได้สร้าง (ต้องสร้างเพิ่ม)
- ยังไม่มี authentication
- ยังไม่มีระบบเก็บประวัติ

## 📞 Support

หากมีปัญหาการใช้งาน:
1. ตรวจสอบ console logs
2. ดู API docs ที่ `/docs`
3. ตรวจสอบ environment variables

---

**Happy Coding! 🎉**
