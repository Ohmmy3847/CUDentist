import httpx

from app.core.config import settings


async def call_risk_service(payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.RISK_SERVICE_URL}/risk_service_api/patient-assessment",
            json=payload,
        )
        response.raise_for_status()
        return response.json()
