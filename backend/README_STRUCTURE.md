# Risk Classification API

Post-Operative Patient Risk Assessment System API

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Application configuration & settings
│   │   └── flows.py            # Risk assessment flow definitions
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models for request/response
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── classification.py   # Classification endpoints
│   │   └── logs.py             # Logging endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── risk_service.py     # Risk classification business logic
│   │   └── log_service.py      # Google Sheets logging service
│   └── utils/
│       └── __init__.py
├── data/                        # Data files (CSV, etc.)
├── logs/                        # Application logs
├── main.py                      # Main application entry point
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── .env                         # Environment variables (not in git)
└── README_STRUCTURE.md          # This file
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with required variables:
```env
GOOGLE_API_KEY=your_google_api_key
MODEL_NAME=gemini-2.0-flash-lite
GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account", ...}
SPREADSHEET_ID=your_spreadsheet_id
FRONTEND_URL=https://your-frontend.vercel.app
```

3. Run the application:
```bash
# Run the server
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Classification
- `GET /` - API information
- `GET /flows` - List available risk assessment flows
- `POST /classify` - Classify single patient (single flow)
- `POST /classify-all-flows` - Classify single patient (all flows)
- `POST /classify-csv` - Batch process CSV file

### Logging
- `POST /log/submission` - Log form submission with results
- `POST /log/raw-input` - Log raw form input

## Development

### Running Tests
```bash
pytest
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Document functions with docstrings

### Adding New Flow
1. Add flow definition in `app/core/flows.py`
2. Flow will be automatically available in all classification endpoints

## Migration from Old Structure

Old files are preserved:
- `flow.py` → `app/core/flows.py`
- `riskClassification.py` → `app/services/risk_service.py`
- `log_form.py` → `app/services/log_service.py`
- `main.py` → `main_new.py` (restructured)

Old files have been moved to `_backup_old_structure/` folder.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| GOOGLE_API_KEY | Google Gemini API key | Yes |
| MODEL_NAME | LLM model name | No (default: gemini-2.0-flash-lite) |
| GOOGLE_SERVICE_ACCOUNT_JSON | Google Sheets service account JSON | Yes (for logging) |
| SPREADSHEET_ID | Google Sheets spreadsheet ID | Yes (for logging) |
| FRONTEND_URL | Frontend URL for CORS | No |

## Deployment

### Render
1. Connect GitHub repository
2. Set environment variables in Render dashboard
3. Deploy from `main` branch
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Docker
```bash
docker build -t risk-api .
docker run -p 8000:8000 --env-file .env risk-api
```
