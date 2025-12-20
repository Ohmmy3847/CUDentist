# Frontend Library Structure

โครงสร้างใหม่ของ `lib/` ที่แยกเป็นระเบียบ

## 📁 โครงสร้างใหม่

```
lib/
├── api/                      # API Clients
│   ├── risk-api.ts          # Risk classification API
│   └── index.ts             # Export all API clients
│
├── types/                    # TypeScript Types
│   ├── form.types.ts        # Form data types & options
│   ├── api.types.ts         # API response types
│   └── index.ts             # Export all types
│
├── utils/                    # Utility Functions (สำหรับอนาคต)
│   └── ...
│
├── hooks/                    # Custom React Hooks (สำหรับอนาคต)
│   └── ...
│
└── index.ts                  # Central export point
```

## 📝 ไฟล์ที่สร้าง

### 1. Types (แยกจาก types.ts เดิม)

#### `lib/types/form.types.ts`
- `PatientFormData` interface (27 fields)
- Form options constants (GENDER_OPTIONS, PROCEDURE_OPTIONS, etc.)

#### `lib/types/api.types.ts`
- `RiskAssessmentResult` interface
- `AllFlowsResult` interface
- `ApiError` interface
- `ProgressCallback` type
- `UploadProgressCallback` type

#### `lib/types/index.ts`
- Export ทั้งหมดจาก form.types และ api.types

### 2. API (ย้ายจาก api.ts เดิม)

#### `lib/api/risk-api.ts`
- `riskApi.classifyPatient()`
- `riskApi.uploadCSV()`
- `riskApi.getFlows()`
- `riskApi.healthCheck()`

#### `lib/api/index.ts`
- Export `riskApi`
- Export `api` (backward compatibility)

### 3. Main Export

#### `lib/index.ts`
- Export ทั้งหมดจาก `api/` และ `types/`
- Central point สำหรับ import

## ✅ Backward Compatibility

**ไม่ต้องแก้โค้ดเดิม!** ยังใช้ import แบบเดิมได้:

```typescript
// ✅ ยังใช้ได้
import { api } from '@/lib/api';
import type { PatientFormData } from '@/lib/types';

// ✅ หรือใช้แบบใหม่
import { api } from '@/lib';
import type { PatientFormData } from '@/lib';
```

## 🎯 ข้อดี

1. **แยกชัดเจน** - types แยกจาก API logic
2. **หาง่าย** - รู้ทันทีว่าไฟล์อยู่ที่ไหน
3. **ขยายง่าย** - เพิ่ม API client ใหม่ได้ง่าย
4. **Maintainable** - แก้ไขที่เดียว ใช้ได้ทุกที่

## 🚀 การใช้งาน

### Import Types
```typescript
import type { 
  PatientFormData,
  RiskAssessmentResult,
  AllFlowsResult 
} from '@/lib';
```

### Import API
```typescript
import { api } from '@/lib';

// Use API
const result = await api.classifyPatient(formData);
```

### Import Constants
```typescript
import { 
  GENDER_OPTIONS,
  PROCEDURE_OPTIONS 
} from '@/lib';
```

## 📦 สำหรับอนาคต

### Utils (เมื่อมี utility functions)
```typescript
// lib/utils/validators.ts
export const validateHN = (hn: string): boolean => {
  return /^\d{10}$/.test(hn);
};

// lib/utils/formatters.ts
export const formatDate = (date: string): string => {
  return new Date(date).toLocaleDateString('th-TH');
};
```

### Hooks (เมื่อมี custom hooks)
```typescript
// lib/hooks/useForm.ts
export const usePatientForm = () => {
  // Form state management
};

// lib/hooks/useApi.ts
export const useRiskClassification = () => {
  // API call with loading/error states
};
```

---

**Created:** December 20, 2025  
**Status:** ✅ Complete & Backward Compatible  
**Breaking Changes:** None - All existing imports still work!
