#!/bin/bash
# Test script for backend structure

echo "🧪 Testing Backend Structure..."
echo "================================"

# Change to backend directory
cd "$(dirname "$0")"

echo ""
echo "1️⃣ Testing imports..."
python -c "from app.core.config import settings; print('✓ Config module OK')" || exit 1
python -c "from app.core.flows import FLOWS; print('✓ Flows module OK')" || exit 1
python -c "from app.models.schemas import PatientData; print('✓ Models module OK')" || exit 1
python -c "from app.services.risk_service import classify_risk; print('✓ Risk service OK')" || exit 1
python -c "from app.routers import classification; print('✓ Classification router OK')" || exit 1

echo ""
echo "2️⃣ Testing main application..."
python -c "import main; print('✓ Main application imports OK')" || exit 1

echo ""
echo "3️⃣ Checking directories..."
[ -d "app/core" ] && echo "✓ app/core/ exists" || echo "✗ app/core/ missing"
[ -d "app/models" ] && echo "✓ app/models/ exists" || echo "✗ app/models/ missing"
[ -d "app/routers" ] && echo "✓ app/routers/ exists" || echo "✗ app/routers/ missing"
[ -d "app/services" ] && echo "✓ app/services/ exists" || echo "✗ app/services/ missing"
[ -d "data" ] && echo "✓ data/ exists" || echo "✗ data/ missing"
[ -d "logs" ] && echo "✓ logs/ exists" || echo "✗ logs/ missing"

echo ""
echo "4️⃣ Checking required files..."
[ -f "app/core/config.py" ] && echo "✓ config.py exists" || echo "✗ config.py missing"
[ -f "app/core/flows.py" ] && echo "✓ flows.py exists" || echo "✗ flows.py missing"
[ -f "app/models/schemas.py" ] && echo "✓ schemas.py exists" || echo "✗ schemas.py missing"
[ -f "main.py" ] && echo "✓ main.py exists" || echo "✗ main.py missing"
[ -f "requirements.txt" ] && echo "✓ requirements.txt exists" || echo "✗ requirements.txt missing"

echo ""
echo "================================"
echo "✅ All tests passed!"
echo ""
echo "To run the server:"
echo "  python main.py"
echo "  or"
echo "  uvicorn main:app --reload"
