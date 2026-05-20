# Website Backend (`backend/`)

This service is the **website backend** (DB-facing). It is separate from the AI microservice in `risk_service_api/`.

## Run (local)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

- Base path: `http://localhost:8001/backend`
- Docs: `http://localhost:8001/backend/docs`
- Health: `http://localhost:8001/backend/health`

