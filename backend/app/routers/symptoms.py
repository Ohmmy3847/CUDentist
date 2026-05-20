from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.symptom import Symptom
from app.models.user import User
from app.schemas.symptom import SymptomCreate, SymptomOut, SymptomUpdate
import httpx
from fastapi import BackgroundTasks
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/symptoms", tags=["symptoms"])

async def _sync_symptom_to_risk_service(
    symptom_id: int, symptom_name: str, risk_level: str,
    recommendation: str = "", management: str = "",
    aliases: list[str] | None = None, action: str = "upsert"
):
    try:
        payload = {
            "symptom_id": symptom_id,
            "symptom_name": symptom_name,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "management": management,
            "aliases": aliases or [],
            "action": action,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.RISK_SERVICE_URL}/risk_service_api/symptoms/sync",
                json=payload,
                timeout=5.0,
            )
            response.raise_for_status()
            logger.info(f"Synced symptom {symptom_id} ({action})")
    except Exception as e:
        logger.error(f"Failed to sync symptom {symptom_id}: {e}")


@router.get("", response_model=list[SymptomOut])
async def list_symptoms(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Symptom).offset(skip).limit(limit))
    return result.scalars().all()


@router.post("", response_model=SymptomOut, status_code=status.HTTP_201_CREATED)
async def create_symptom(
    body: SymptomCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    symptom = Symptom(**body.model_dump(), managed_by=current_user.user_id)
    db.add(symptom)
    await db.commit()
    await db.refresh(symptom)
    
    background_tasks.add_task(
        _sync_symptom_to_risk_service,
        symptom_id=symptom.symptom_id,
        symptom_name=symptom.symptom_name,
        risk_level=symptom.risk_level,
        recommendation=symptom.recommendation or "",
        management=symptom.management_guidance or "",
        aliases=symptom.aliases or [],
    )
    return symptom


@router.patch("/{symptom_id}", response_model=SymptomOut)
async def update_symptom(
    symptom_id: int,
    body: SymptomUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    symptom = await db.get(Symptom, symptom_id)
    if not symptom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symptom not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(symptom, field, value)
    await db.commit()
    await db.refresh(symptom)
    background_tasks.add_task(
        _sync_symptom_to_risk_service,
        symptom_id=symptom.symptom_id,
        symptom_name=symptom.symptom_name,
        risk_level=symptom.risk_level,
        recommendation=symptom.recommendation or "",
        management=symptom.management_guidance or "",
        aliases=symptom.aliases or [],
    )
    return symptom


@router.delete("/{symptom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_symptom(
    symptom_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    symptom = await db.get(Symptom, symptom_id)
    if not symptom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symptom not found")
    await db.delete(symptom)
    await db.commit()
    
    background_tasks.add_task(
        _sync_symptom_to_risk_service,
        symptom_id=symptom_id,
        symptom_name="",
        risk_level="",
        action="delete",
    )


@router.post("/resync", status_code=status.HTTP_202_ACCEPTED)
async def resync_symptoms(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Rebuild the ChromaDB 'symptoms' collection from the current PostgreSQL data."""
    result = await db.execute(select(Symptom))
    all_symptoms = result.scalars().all()

    payload = {
        "symptoms": [
            {
                "symptom_id": s.symptom_id,
                "symptom_name": s.symptom_name,
                "risk_level": s.risk_level,
                "recommendation": s.recommendation or "",
                "management": s.management_guidance or "",
                "action": "upsert",
            }
            for s in all_symptoms
        ]
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{settings.RISK_SERVICE_URL}/risk_service_api/symptoms/rebuild",
                json=payload,
            )
            resp.raise_for_status()
    except Exception as e:
        logger.error(f"Symptom resync failed: {e}")
        raise HTTPException(status_code=502, detail="Failed to reach risk service")

    return {"status": "accepted", "count": len(all_symptoms)}
