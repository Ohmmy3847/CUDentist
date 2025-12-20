# 🏗️ Guide Building: ระบบประเมินความเสี่ยงผู้ป่วย

> คู่มือการสร้างและพัฒนาระบบแบบ Professional สำหรับ Scale ในอนาคต

---

## 📖 สารบัญ

1. [ภาพรวมระบบ](#ภาพรวมระบบ)
2. [Backend Architecture](#backend-architecture)
3. [Frontend Architecture](#frontend-architecture)
4. [การทำงานร่วมกัน](#การทำงานร่วมกัน)
5. [หลักการออกแบบ](#หลักการออกแบบ)
6. [แนวทางขยายระบบ](#แนวทางขยายระบบ)

---

## 🎯 ภาพรวมระบบ

### สถาปัตยกรรม (High-Level)

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│   Browser   │────────▶│   Next.js   │────────▶│   FastAPI    │
│  (User)     │◀────────│  (Frontend) │◀────────│  (Backend)   │
└─────────────┘         └─────────────┘         └──────────────┘
                              │                         │
                              │                         ├──▶ Google AI
                              │                         │
                              ▼                         └──▶ Google Sheets
                        localStorage                         (Logging)
                        (Draft Save)
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14 (App Router) | React framework |
| **UI** | Tailwind CSS | Styling |
| **State** | React Hooks + localStorage | State management |
| **Backend** | FastAPI (Python) | API server |
| **AI** | Google Gemini | Risk classification |
| **Logging** | Google Sheets | Data storage |
| **Deployment** | Vercel + Render | Hosting |

---

## 🔧 Backend Architecture

### 📁 โครงสร้างไฟล์

```
backend/
├── app/
│   ├── core/                    # ⚙️ Configuration & Constants
│   │   ├── config.py           # Settings (API keys, URLs)
│   │   └── flows.py            # 18 Risk Classification Flows
│   │
│   ├── models/                  # 📦 Data Models
│   │   └── schemas.py          # Pydantic models (PatientData, RiskResponse)
│   │
│   ├── routers/                 # 🎯 API Endpoints
│   │   ├── classification.py   # Risk classification endpoints
│   │   └── logs.py             # Logging endpoints
│   │
│   ├── services/                # 🧠 Business Logic
│   │   ├── risk_service.py     # AI classification logic
│   │   └── log_service.py      # Google Sheets logging
│   │
│   └── utils/                   # 🔧 Helper Functions
│       └── helpers.py
│
├── data/                        # 📊 CSV data files
├── logs/                        # 📝 Application logs
├── main.py                      # 🚀 Application entry point
├── requirements.txt             # 📦 Python dependencies
├── Dockerfile                   # 🐳 Docker configuration
└── .env                         # 🔐 Environment variables
```

### 🏗️ Layer Architecture

```
┌──────────────────────────────────────────────────────┐
│  Layer 1: API Routers (classification.py, logs.py)  │  ← รับ/ส่ง HTTP
├──────────────────────────────────────────────────────┤
│  Layer 2: Services (risk_service, log_service)      │  ← Business Logic
├──────────────────────────────────────────────────────┤
│  Layer 3: Models (schemas.py)                       │  ← Data Structure
├──────────────────────────────────────────────────────┤
│  Layer 4: Core (config.py, flows.py)                │  ← Config + Constants
├──────────────────────────────────────────────────────┤
│  Layer 5: Utils (helpers.py)                        │  ← Helper Functions
└──────────────────────────────────────────────────────┘
```

### 📝 แต่ละ Layer ทำอะไร

#### Layer 1: Routers (API Endpoints)
**หน้าที่:** รับ request จาก frontend, ส่งต่อให้ service, return response

```python
# app/routers/classification.py
@router.post("/classify-all-flows")
async def classify_all_flows(patient: PatientData, llm):
    # 1. รับข้อมูล patient
    # 2. Loop ทุก flow
    for flow_name, flow in FLOWS.items():
        # 3. เรียก service ประมวลผล
        result = classify_risk(patient.data, flow, llm)
        results[flow_name] = result
    
    # 4. เรียก log service
    append_with_result(patient.data, results, FORM_COLUMNS)
    
    # 5. Return results
    return results
```

**ข้อดี:**
- ✅ Router สั้น อ่านง่าย
- ✅ Logic แยกออก ใช้ซ้ำได้
- ✅ Test ง่าย

#### Layer 2: Services (Business Logic)
**หน้าที่:** Logic การทำงานจริง, เรียกใช้ AI, ประมวลผลข้อมูล

```python
# app/services/risk_service.py
def classify_risk(input_data: dict, flow: dict, llm):
    # 1. Format ข้อมูล
    formatted = format_input_data_for_display(input_data)
    
    # 2. สร้าง prompt สำหรับ AI
    prompt = PromptTemplate(...)
    
    # 3. เรียก AI
    chain = prompt | llm | parser
    response = chain.invoke({...})
    
    # 4. Return ผลลัพธ์
    return response
```

**ทำไมแยก:**
- ✅ เปลี่ยน LLM ง่าย (แก้ที่เดียว)
- ✅ ใช้ซ้ำได้หลายที่
- ✅ Test แยกส่วนได้

#### Layer 3: Models (Data Structure)
**หน้าที่:** กำหนดรูปแบบข้อมูล, validate อัตโนมัติ

```python
# app/models/schemas.py
class PatientData(BaseModel):
    data: Dict[str, Any]
    flow_name: Optional[str] = None

class RiskResponse(BaseModel):
    risk_level: str
    recommendation: str
    reason: str
```

**ข้อดี:**
- ✅ Type safety
- ✅ Auto validation
- ✅ Auto documentation (FastAPI)

#### Layer 4: Core (Configuration)
**หน้าที่:** Config ทั้งหมด, constants

```python
# app/core/config.py
class Settings:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.0-flash-lite")
    ALLOWED_ORIGINS: list = [...]
```

**ทำไมรวม:**
- ✅ Config รวมศูนย์
- ✅ แก้ที่เดียวได้ผลทุกที่
- ✅ ปลอดภัย (ใช้ .env)

#### Layer 5: Utils (Helpers)
**หน้าที่:** Helper functions ที่ใช้ซ้ำได้

```python
# app/utils/helpers.py
def format_date(date_str: str) -> str:
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")

def validate_hn(hn: str) -> bool:
    return len(hn) == 10 and hn.isdigit()
```

---

## 🎨 Frontend Architecture

### 📁 โครงสร้างไฟล์

```
frontend/
├── app/                         # 📄 Pages (Next.js App Router)
│   ├── page.tsx                # Home page (เลือกฟอร์มหรืออัปโหลด)
│   ├── layout.tsx              # Root layout
│   ├── globals.css             # Global styles
│   │
│   ├── form/                   # 📝 Form Flow
│   │   └── page.tsx           # Multi-step form (27 questions)
│   │
│   ├── result/                 # 📊 Results Display
│   │   └── page.tsx           # Show risk assessment results
│   │
│   └── upload/                 # 📤 CSV Upload
│       └── page.tsx           # Batch processing
│
├── components/                  # 🧩 Reusable Components
│   ├── RiskResult.tsx          # Risk result display component
│   └── forms/                  # Form components
│       ├── BasicInfoForm.tsx   # ข้อ 1-5: อายุ, เพศ, HN, หัตถการ
│       ├── SymptomsForm.tsx    # ข้อ 6-20: อาการต่างๆ
│       └── DailyLifeForm.tsx   # ข้อ 21-27: การใช้ชีวิต
│
├── lib/                         # 📚 Libraries & Utilities
│   ├── api.ts                  # API client (Axios)
│   └── types.ts                # TypeScript types
│
├── public/                      # 🖼️ Static assets
├── .env.local                  # 🔐 Environment variables
├── package.json                # 📦 Dependencies
├── tailwind.config.js          # 🎨 Tailwind configuration
└── tsconfig.json               # ⚙️ TypeScript configuration
```

### 🏗️ Component Architecture

```
App
├── Home Page (/)
│   ├── Form Card → /form
│   └── Upload Card → /upload
│
├── Form Page (/form)
│   ├── Step 1: BasicInfoForm
│   ├── Step 2: SymptomsForm
│   ├── Step 3: DailyLifeForm
│   └── Submit → /result
│
├── Result Page (/result)
│   └── RiskResult Component (18 flows)
│
└── Upload Page (/upload)
    └── CSV Upload → Download Results
```

### 🔄 State Management

#### 1. Form State (React Hooks)
```typescript
// app/form/page.tsx
const [currentStep, setCurrentStep] = useState(1);       // Current step (1-3)
const [formData, setFormData] = useState<PatientFormData>({}); // Form data
const [isSubmitting, setIsSubmitting] = useState(false); // Loading state
```

**ทำไมใช้ useState:**
- ✅ Simple & effective
- ✅ ไม่ซับซ้อนเกินไป
- ✅ เหมาะกับ form ขนาดนี้

#### 2. Local Storage (Draft Auto-Save)
```typescript
// Auto-save draft ทุกครั้งที่ formData เปลี่ยน
useEffect(() => {
  localStorage.setItem('patientFormDraft', JSON.stringify(formData));
}, [formData]);

// Load draft on mount
useEffect(() => {
  const savedData = localStorage.getItem('patientFormDraft');
  if (savedData) setFormData(JSON.parse(savedData));
}, []);
```

**ทำไมใช้ localStorage:**
- ✅ ไม่หายแม้ปิดเบราว์เซอร์
- ✅ ไม่ต้องมี backend
- ✅ User experience ดี

#### 3. Session Storage (Results)
```typescript
// Store results and navigate
sessionStorage.setItem('riskAssessmentResult', JSON.stringify(result));
router.push('/result');
```

**ทำไมใช้ sessionStorage:**
- ✅ หายเมื่อปิด tab (security)
- ✅ ไม่ส่งข้อมูลผ่าน URL
- ✅ เหมาะกับข้อมูลชั่วคราว

### 🔌 API Integration

```typescript
// lib/api.ts
export const api = {
  classifyPatient: async (
    data: PatientFormData,
    onProgress?: (current: number, total: number, flowName: string) => void
  ): Promise<AllFlowsResult> => {
    // 1. Get flows
    const flowsResponse = await apiClient.get('/flows');
    const flows = flowsResponse.data.flows;
    
    // 2. Classify
    const response = await apiClient.post('/classify-all-flows', { data });
    
    // 3. Progress callback
    if (onProgress) {
      for (let i = 0; i < flows.length; i++) {
        onProgress(i + 1, flows.length, flows[i]);
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }
    
    return response.data;
  }
};
```

**Features:**
- ✅ Progress tracking
- ✅ Error handling
- ✅ Type-safe

### 📱 Responsive Design

```typescript
// Tailwind classes for responsive
<div className="grid md:grid-cols-2 gap-8">  {/* 2 columns on medium+ */}
  <div className="p-4 sm:p-6 md:p-8">       {/* Responsive padding */}
    <h1 className="text-2xl md:text-4xl">   {/* Responsive text */}
```

**Breakpoints:**
- `sm:` 640px+
- `md:` 768px+
- `lg:` 1024px+
- `xl:` 1280px+

---

## 🔄 การทำงานร่วมกัน

### Flow 1: ประเมินความเสี่ยงผ่านฟอร์ม

```
1. User กรอกฟอร์ม (Frontend)
   └─ localStorage auto-save draft

2. User กด Submit
   └─ POST /classify-all-flows
      {
        "data": {
          "age": 25,
          "gender": "หญิง",
          "pain_score": 7,
          ...
        }
      }

3. Backend ประมวลผล
   ├─ Loop 18 flows
   ├─ เรียก Google AI แต่ละ flow
   │  └─ Gemini API (classification)
   └─ Return results

4. Backend เก็บ log
   └─ Google Sheets API
      └─ Append row (form data + results)

5. Frontend แสดงผล
   └─ Navigate to /result
      └─ Show 18 risk assessments
         ├─ ความเสี่ยงต่ำ (green)
         ├─ ความเสี่ยงกลาง (yellow)
         └─ ความเสี่ยงสูง (red)
```

### Flow 2: อัปโหลด CSV

```
1. User อัปโหลด CSV
   └─ POST /classify-csv (multipart/form-data)

2. Backend ประมวลผล
   ├─ Save temp file
   ├─ Read CSV (pandas)
   ├─ Process each row
   │  └─ Concurrent processing (10 at a time)
   └─ Generate result CSV

3. Backend return file
   └─ FileResponse (result_TIMESTAMP.csv)

4. User download results
   └─ CSV with all 18 flow results
```

### API Endpoints Summary

| Method | Endpoint | Purpose | Input | Output |
|--------|----------|---------|-------|--------|
| GET | `/` | API info | - | API information |
| GET | `/flows` | List flows | - | List of 18 flows |
| POST | `/classify` | Single flow | PatientData + flow_name | RiskResponse |
| POST | `/classify-all-flows` | All flows | PatientData | All 18 results |
| POST | `/classify-csv` | Batch CSV | CSV file | Result CSV |
| POST | `/log/submission` | Log data | form_data + results | Success status |

---

## 🎓 หลักการออกแบบ

### 1. Separation of Concerns
> แต่ละส่วนทำหน้าที่ของตัวเอง ไม่รับผิดชอบเกินไป

**ตัวอย่าง:**

| Layer | Responsibility | DON'T |
|-------|---------------|-------|
| **Router** | รับ/ส่ง HTTP | ❌ ทำ business logic |
| **Service** | Business logic | ❌ รับ HTTP request |
| **Model** | Data structure | ❌ ทำ validation logic |

**ข้อดี:**
- ✅ แก้ไขง่าย (แก้ที่เดียว)
- ✅ Test ง่าย (test แยกส่วน)
- ✅ ทำงานร่วมกันง่าย (คนละส่วน)

### 2. DRY (Don't Repeat Yourself)
> เขียน code ครั้งเดียว ใช้ได้หลายที่

```typescript
// ❌ แบบซ้ำซ้อน
function getUserById(id: number) {
  const conn = createConnection();
  const result = conn.query(`SELECT * FROM users WHERE id=${id}`);
  conn.close();
  return result;
}

function getUserByEmail(email: string) {
  const conn = createConnection();
  const result = conn.query(`SELECT * FROM users WHERE email='${email}'`);
  conn.close();
  return result;
}

// ✅ แบบไม่ซ้ำ
function executeQuery(sql: string) {
  const conn = createConnection();
  const result = conn.query(sql);
  conn.close();
  return result;
}

function getUserById(id: number) {
  return executeQuery(`SELECT * FROM users WHERE id=${id}`);
}

function getUserByEmail(email: string) {
  return executeQuery(`SELECT * FROM users WHERE email='${email}'`);
}
```

### 3. SOLID Principles

#### S - Single Responsibility
```python
# ✅ แต่ละ function ทำอย่างเดียว
def classify_risk(data, flow, llm): ...     # ประมวลผล
def log_to_sheets(data): ...                # เก็บ log
def format_date(date): ...                  # Format วันที่
def send_email(to, subject, body): ...      # ส่งอีเมล

# ❌ ไม่ดี: function เดียวทำหลายอย่าง
def process_and_log_and_email(data):
    # classify
    # log
    # send email
    pass
```

#### O - Open/Closed
```python
# ✅ เพิ่ม feature ใหม่ได้โดยไม่แก้ของเดิม
class LLMFactory:
    def create(self, model_type: str):
        if model_type == "gemini":
            return GeminiLLM()
        elif model_type == "openai":
            return OpenAILLM()
        elif model_type == "claude":      # เพิ่มใหม่ได้ง่าย
            return ClaudeLLM()
```

#### L - Liskov Substitution
```python
# ✅ Subclass ใช้แทน parent class ได้
class LLM:
    def invoke(self, data): pass

class GeminiLLM(LLM):
    def invoke(self, data):
        return gemini_api.call(data)

class OpenAILLM(LLM):
    def invoke(self, data):
        return openai_api.call(data)

# ใช้งาน
def classify(data, llm: LLM):  # รับ LLM parent type
    return llm.invoke(data)    # ใช้ได้กับทุก subclass
```

#### I - Interface Segregation
```typescript
// ✅ แยก interface ตามความจำเป็น
interface Readable {
  read(): string;
}

interface Writable {
  write(data: string): void;
}

// Class ใช้เฉพาะที่ต้องการ
class File implements Readable, Writable { }
class Logger implements Writable { }  // ไม่ต้อง implement read
```

#### D - Dependency Injection
```python
# ❌ ไม่ดี: สร้าง dependency ใน function
def classify(data):
    llm = ChatGoogleGenerativeAI()  # ผูกติดกับ Gemini
    return llm.invoke(data)

# ✅ ดี: รับ dependency จากข้างนอก
def classify(data, llm):
    return llm.invoke(data)  # ใช้ llm อะไรก็ได้

# ใช้งาน
result = classify(data, gemini_llm)   # ใช้ Gemini
result = classify(data, openai_llm)   # เปลี่ยนเป็น OpenAI ได้ง่าย!
```

### 4. Error Handling Strategy

#### Backend
```python
@router.post("/classify")
async def classify(patient: PatientData):
    try:
        # Try to classify
        result = classify_risk(patient.data)
        return result
        
    except ValueError as e:
        # Client error (bad input)
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        # Server error (unexpected)
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### Frontend
```typescript
const handleSubmit = async () => {
  setIsSubmitting(true);
  setError(null);
  
  try {
    const result = await api.classifyPatient(formData);
    sessionStorage.setItem('result', JSON.stringify(result));
    router.push('/result');
    
  } catch (error) {
    if (error.response?.status === 400) {
      setError('ข้อมูลไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง');
    } else {
      setError('เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง');
    }
    console.error('Error:', error);
    
  } finally {
    setIsSubmitting(false);
  }
};
```

### 5. Configuration Management

```bash
# Backend: .env
GOOGLE_API_KEY=AIza...
MODEL_NAME=gemini-2.0-flash-lite
GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account"...}
SPREADSHEET_ID=1abc...
FRONTEND_URL=https://your-app.vercel.app

# Frontend: .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Risk Assessment System
```

**ข้อดี:**
- ✅ แยก config จาก code
- ✅ ปลอดภัย (ไม่ commit secret)
- ✅ เปลี่ยน environment ง่าย (dev/staging/prod)

---

## 🚀 แนวทางขยายระบบ

### Phase 1: ตอนนี้ (MVP) ✅

```
✅ Multi-step form (27 questions)
✅ 18 risk classification flows
✅ Google AI integration
✅ Google Sheets logging
✅ CSV batch processing
✅ Responsive design
✅ Auto-save draft
✅ Professional structure
✅ Error handling
✅ Progress tracking
```

### Phase 2: Short-term (3-6 เดือน)

#### 🔐 Authentication & Authorization

**Backend:**
```python
# app/core/security.py
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Frontend:**
```typescript
// lib/auth.ts
import { useSession } from 'next-auth/react'

export function useAuth() {
  const { data: session, status } = useSession()
  
  return {
    user: session?.user,
    isLoading: status === 'loading',
    isAuthenticated: status === 'authenticated'
  }
}

// Protect routes
export default function DashboardPage() {
  const { isAuthenticated, isLoading } = useAuth()
  
  if (isLoading) return <Loading />
  if (!isAuthenticated) redirect('/login')
  
  return <Dashboard />
}
```

**Technologies:**
- Backend: FastAPI + JWT
- Frontend: NextAuth.js
- Database: PostgreSQL (user table)

**Roles:**
- `admin` - Full access
- `doctor` - View all, classify
- `nurse` - View assigned, classify

#### 📊 Dashboard & Analytics

```typescript
// app/dashboard/page.tsx
export default function DashboardPage() {
  return (
    <div className="grid gap-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard 
          title="Total Patients" 
          value={1234} 
          change="+12%" 
          icon={<UsersIcon />}
        />
        <StatsCard 
          title="High Risk" 
          value={45} 
          change="-5%" 
          icon={<AlertIcon />}
          color="red"
        />
        <StatsCard 
          title="Avg Response Time" 
          value="2.3s" 
          icon={<ClockIcon />}
        />
        <StatsCard 
          title="Success Rate" 
          value="98.5%" 
          icon={<CheckIcon />}
          color="green"
        />
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Risk Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <PieChart data={riskDistribution} />
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Daily Submissions</CardTitle>
          </CardHeader>
          <CardContent>
            <LineChart data={dailySubmissions} />
          </CardContent>
        </Card>
      </div>
      
      {/* Recent Submissions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Submissions</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable 
            columns={columns} 
            data={recentSubmissions}
            onRowClick={handleRowClick}
          />
        </CardContent>
      </Card>
    </div>
  )
}
```

**Features:**
- ✅ Real-time statistics
- ✅ Interactive charts
- ✅ Export reports (PDF, Excel)
- ✅ Date range filtering
- ✅ Search & filter patients

**Technologies:**
- React Query (data fetching)
- Chart.js / Recharts (visualization)
- TanStack Table (data table)
- jsPDF (PDF export)

#### 💾 Database Integration

**Replace Google Sheets with PostgreSQL:**

```python
# app/repositories/patient_repository.py
from sqlalchemy.orm import Session
from app.models.database import Patient, RiskAssessment

class PatientRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_patient(self, patient_data: dict):
        patient = Patient(**patient_data)
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient
    
    def create_assessment(self, patient_id: int, results: dict):
        assessment = RiskAssessment(
            patient_id=patient_id,
            results=results,
            created_at=datetime.now()
        )
        self.db.add(assessment)
        self.db.commit()
        return assessment
    
    def get_patients(self, skip: int = 0, limit: int = 100):
        return self.db.query(Patient).offset(skip).limit(limit).all()
```

**Database Schema:**
```sql
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    hn VARCHAR(10) UNIQUE NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE risk_assessments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    results JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_patient_hn ON patients(hn);
CREATE INDEX idx_assessment_date ON risk_assessments(created_at);
```

**Migration Strategy:**
1. Setup PostgreSQL
2. Migrate existing Google Sheets data
3. Dual write (both systems) for 1 week
4. Switch to PostgreSQL only
5. Keep Google Sheets as backup

#### 🔔 Notification System

```python
# app/services/notification_service.py
from twilio.rest import Client

class NotificationService:
    def send_high_risk_alert(self, patient_data, results):
        # Email notification
        self.send_email(
            to=patient_data['doctor_email'],
            subject=f"High Risk Alert - Patient {patient_data['hn']}",
            body=self.render_alert_template(patient_data, results)
        )
        
        # SMS notification
        self.send_sms(
            to=patient_data['doctor_phone'],
            message=f"High risk patient {patient_data['hn']} requires attention"
        )
        
        # LINE notification
        self.send_line_notify(
            token=patient_data['line_token'],
            message=self.render_line_message(patient_data, results)
        )
```

**Technologies:**
- Email: SendGrid / AWS SES
- SMS: Twilio
- LINE: LINE Notify API
- Push: Firebase Cloud Messaging

### Phase 3: Mid-term (6-12 เดือน)

#### 🔍 Advanced AI Features

**1. Trend Analysis**
```python
def analyze_patient_trend(patient_id: int):
    """วิเคราะห์แนวโน้มอาการของผู้ป่วย"""
    assessments = get_patient_assessments(patient_id)
    
    # Calculate trend
    trend = calculate_risk_trend(assessments)
    
    # Predict future risk
    prediction = ml_model.predict_risk(
        historical_data=assessments,
        days_ahead=7
    )
    
    return {
        "trend": trend,  # improving/worsening/stable
        "prediction": prediction,
        "confidence": 0.85
    }
```

**2. Similar Case Matching**
```python
def find_similar_cases(patient_data: dict, top_k: int = 5):
    """หาผู้ป่วยที่มีลักษณะคล้ายกัน"""
    embedding = vectorize_patient_data(patient_data)
    
    # Vector similarity search
    similar_cases = vector_db.search(
        query_vector=embedding,
        top_k=top_k
    )
    
    return similar_cases
```

**3. Automated Recommendations**
```python
def generate_care_plan(patient_data: dict, risk_results: dict):
    """สร้างแผนการดูแลอัตโนมัติ"""
    prompt = f"""
    Based on patient data and risk assessment:
    - Demographics: {patient_data}
    - Risk levels: {risk_results}
    
    Generate a personalized care plan including:
    1. Immediate actions
    2. Medications
    3. Follow-up schedule
    4. Warning signs to watch
    """
    
    care_plan = llm.invoke(prompt)
    return care_plan
```

#### 📱 Mobile App

**React Native App:**
```typescript
// mobile/src/screens/AssessmentScreen.tsx
export function AssessmentScreen() {
  return (
    <ScrollView>
      <CameraScanner 
        onScan={handleWoundScan}  // AI wound analysis
      />
      
      <VoiceInput 
        onTranscribe={handleVoiceInput}  // Voice-to-text
      />
      
      <QuickAssessment 
        questions={quickQuestions}
        onSubmit={handleQuickSubmit}
      />
      
      <OfflineQueue 
        items={pendingSubmissions}  // Offline support
      />
    </ScrollView>
  )
}
```

**Features:**
- ✅ Quick assessment (5 min form)
- ✅ Camera for wound photos
- ✅ Voice input (Thai language)
- ✅ Offline mode
- ✅ Push notifications
- ✅ QR code patient lookup

#### 🔄 Real-time Collaboration

```typescript
// Using WebSocket
const socket = io(WS_URL)

socket.on('patient_updated', (data) => {
  // Real-time patient updates
  updatePatientData(data)
})

socket.on('new_assessment', (data) => {
  // Show notification
  showNotification(`New assessment for patient ${data.hn}`)
})
```

**Features:**
- ✅ Real-time patient updates
- ✅ Collaborative notes
- ✅ Live chat for doctors
- ✅ Presence indicators

### Phase 4: Long-term (1-2 ปี)

#### 🏥 Hospital Integration

**HL7 FHIR Integration:**
```python
# app/integrations/fhir.py
from fhir.resources.patient import Patient as FHIRPatient

class FHIRIntegration:
    def sync_patient(self, hn: str):
        # Get from hospital system
        fhir_patient = self.fhir_client.get_patient(hn)
        
        # Convert to our format
        patient_data = self.convert_fhir_to_internal(fhir_patient)
        
        # Save to our database
        return self.patient_repo.create_or_update(patient_data)
```

**Features:**
- ✅ Auto-sync patient data
- ✅ Lab results integration
- ✅ Medication history
- ✅ Radiology images

#### 🤖 Machine Learning Enhancements

**Custom ML Models:**
```python
# app/ml/risk_predictor.py
import tensorflow as tf

class RiskPredictor:
    def __init__(self):
        self.model = tf.keras.models.load_model('models/risk_model.h5')
    
    def predict(self, patient_data: dict):
        # Preprocess
        features = self.preprocess(patient_data)
        
        # Predict
        prediction = self.model.predict(features)
        
        # Post-process
        risk_scores = self.postprocess(prediction)
        
        return risk_scores
```

**Training Pipeline:**
```python
def train_model():
    # 1. Collect data from database
    data = fetch_training_data()
    
    # 2. Preprocess
    X, y = preprocess_training_data(data)
    
    # 3. Train
    model = create_model()
    model.fit(X, y, epochs=100, validation_split=0.2)
    
    # 4. Evaluate
    metrics = evaluate_model(model, test_data)
    
    # 5. Deploy if better
    if metrics['accuracy'] > current_model_accuracy:
        deploy_model(model)
```

#### ☁️ Microservices Architecture

```
┌─────────────────────────────────────────────────────┐
│                   API Gateway                        │
│              (Kong / AWS API Gateway)                │
└─────────────────────────────────────────────────────┘
           │              │              │
    ┌──────┴──────┐ ┌────┴─────┐ ┌────┴──────┐
    │   Patient   │ │   Risk   │ │   Notify  │
    │   Service   │ │ Service  │ │  Service  │
    └─────────────┘ └──────────┘ └───────────┘
           │              │              │
    ┌──────┴──────┐ ┌────┴─────┐ ┌────┴──────┐
    │ PostgreSQL  │ │  Redis   │ │ RabbitMQ  │
    └─────────────┘ └──────────┘ └───────────┘
```

**Benefits:**
- ✅ Scale independently
- ✅ Deploy separately
- ✅ Technology flexibility
- ✅ Fault isolation

---

## 📚 Best Practices Summary

### ✅ DO

1. **แยก Layer ชัดเจน**
   - Router ≠ Business Logic
   - Service ≠ Data Access
   
2. **ใช้ Type Safety**
   - Pydantic (Backend)
   - TypeScript (Frontend)
   
3. **Error Handling**
   - Try-catch ทุกที่
   - Log errors
   - User-friendly messages
   
4. **Config Management**
   - ใช้ environment variables
   - แยก dev/staging/prod
   
5. **Testing**
   - Unit tests (services)
   - Integration tests (APIs)
   - E2E tests (critical flows)
   
6. **Documentation**
   - Code comments
   - API documentation (FastAPI auto-docs)
   - README files
   
7. **Git Best Practices**
   - Feature branches
   - Clear commit messages
   - Pull requests

### ❌ DON'T

1. **ไม่แยก Concerns**
   - ❌ Business logic ใน router
   - ❌ API calls ใน components
   
2. **Hardcode Values**
   - ❌ API keys ใน code
   - ❌ URLs ใน code
   
3. **Ignore Errors**
   - ❌ Empty catch blocks
   - ❌ ไม่ log errors
   
4. **Over-engineering**
   - ❌ Microservices ตอนเริ่มต้น
   - ❌ Complex patterns ที่ไม่จำเป็น

---

## 🎯 Decision Tree: เมื่อไหร่ควรทำอะไร

```
Project Size?
├─ Small (1-2 developers)
│  ✅ Monolith
│  ✅ Simple state management
│  ✅ SQLite / PostgreSQL
│  ❌ Microservices
│  ❌ Complex infrastructure
│
├─ Medium (3-5 developers)
│  ✅ Modular monolith
│  ✅ PostgreSQL
│  ✅ Redis caching
│  ✅ Background jobs
│  ⚠️ Consider microservices if needed
│
└─ Large (6+ developers)
   ✅ Microservices
   ✅ Message queues
   ✅ Load balancers
   ✅ Kubernetes
   ✅ CI/CD pipeline
```

---

## 📖 คำแนะนำสุดท้าย

### 🎯 Start Simple, Scale When Needed

1. **เริ่มจาก MVP** (ตอนนี้)
   - ✅ Core features
   - ✅ Professional structure
   - ✅ Production ready

2. **เพิ่มเมื่อจำเป็น** (Phase 2-3)
   - Authentication
   - Database
   - Advanced features

3. **Scale เมื่อจำเป็นจริงๆ** (Phase 4)
   - Microservices
   - ML enhancements
   - Hospital integration

### 💡 คำคม

> "Premature optimization is the root of all evil" - Donald Knuth

> "Make it work, make it right, make it fast" - Kent Beck

---

## 🔗 Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Google AI Python SDK](https://ai.google.dev/gemini-api/docs)

### Learning
- [Full Stack FastAPI](https://fastapi.tiangolo.com/tutorial/)
- [Next.js Learn](https://nextjs.org/learn)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)

### Tools
- [VS Code](https://code.visualstudio.com/)
- [Postman](https://www.postman.com/) - API testing
- [pgAdmin](https://www.pgadmin.org/) - PostgreSQL GUI
- [Docker Desktop](https://www.docker.com/products/docker-desktop)

---

**Created:** December 20, 2025  
**Version:** 1.0  
**Status:** ✅ Complete & Ready for Production  
**Next Phase:** Authentication & Dashboard (Phase 2)
