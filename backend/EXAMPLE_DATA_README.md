# Patient Assessment Example Data

## Example Request Files

### Thai Language Example
- **File**: `example_request.json`
- **Language**: Thai (th)
- Example patient data with Thai text for testing the API

### English Language Example  
- **File**: `example_request_en.json`
- **Language**: English (en)
- Example patient data with English text for testing the API

## How to Test

### Using curl:
```bash
curl -X POST http://localhost:8000/patient-assessment \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

### Using Python:
```python
import requests
import json

with open('example_request.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

response = requests.post(
    'http://localhost:8000/patient-assessment',
    json=data
)

print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

## Risk Levels

The system uses the following risk levels (from `backend/app/services/flow_parser.py`):

- **ความเสี่ยงต่ำ** (LOW) - Low risk, normal symptoms
- **ความเสี่ยงปานกลาง** (MEDIUM) - Moderate risk, requires observation
- **ความเสี่ยงสูง** (HIGH) - High risk, requires immediate attention
- **ไม่สามารถสรุปผลความเสี่ยงได้เนื่องจากอาการมีความซับซ้อน** (COMPLICATED) - Complex symptoms requiring doctor consultation
- **ไม่สามารถประเมินได้** (UNKNOWN) - Cannot assess with given data
- **ไม่ต้องประเมิน** (NOT_APPLICABLE) - Not applicable for this patient

## Response Structure

```json
{
  "patient": {
    "basic_info": { ... },
    "assessment_data": { ... }
  },
  "flows": {
    "ระดับความปวด ณ ปัจจุบัน (Pain score)": {
      "risk_level": "ความเสี่ยงต่ำ",
      "recommendation": "ติดตามอาการต่อไป...",
      "reason": "Pain score 5/10..."
    },
    ...
  },
  "summary": {
    "overall_risk": "ความเสี่ยงต่ำ",
    "critical_issues": [],
    "summary": "ผู้ป่วยฟื้นตัวดีตามปกติ..."
  },
  "errors": null
}
```

**Note:** 
- `additional_questions` field can be included in the request but the response will not include `patient_qa`. 
- Patient Q&A is handled separately via a different endpoint.
- The `additional_questions` data is still saved for record-keeping purposes.

## Field Changes (v2.0)

**Removed Fields:**
- `email` - Email address (not needed for assessment)
- `birth_year` - Birth year in Buddhist Era
- `age` - Age in years

**Added Fields:**
- `birth_date` - Date of birth in ISO format (YYYY-MM-DD)

This allows the system to calculate age accurately and eliminates redundant fields.
