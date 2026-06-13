import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_user, get_db, require_permission
from app.models.form_token import FormToken
from app.models.patient import Patient
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientOut, PatientUpdate
from app.services.audit_service import audit
from app.services.email_service import send_new_case_email

router = APIRouter(prefix="/patients", tags=["patients"])


def _norm_schedule(s: str | None) -> str | None:
    """Normalize ISO datetime string to consistent +00:00 format."""
    if not s:
        return s
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    except ValueError:
        return s


def _make_token(patient_hn: str, schedule_date: str | None, now: datetime, expire_days: int) -> FormToken:
    token_str = str(uuid.uuid4())
    plain_password = token_str[:6]
    return FormToken(
        token=token_str,
        patient_hn=patient_hn,
        schedule_date=schedule_date,
        password_hash=hashlib.sha256(plain_password.encode()).hexdigest(),
        expires_at=now + timedelta(days=expire_days),
        created_at=now,
    )


async def _ensure_tokens_for_patient(patient: Patient, db: AsyncSession) -> None:
    """Create tokens for any schedule that doesn't have one yet."""
    now = datetime.now(timezone.utc)
    schedules = [_norm_schedule(s) for s in (patient.follow_up_schedules or []) if s]

    existing = (await db.execute(
        select(FormToken.schedule_date).where(
            FormToken.patient_hn == patient.hn,
            FormToken.is_used == False,  # noqa: E712
        )
    )).scalars().all()
    existing_set = {_norm_schedule(s) for s in existing if s}

    for sched in schedules:
        if sched not in existing_set:
            db.add(_make_token(patient.hn, sched, now, settings.FORM_TOKEN_EXPIRE_DAYS))


async def _patient_out(patient: Patient, db: AsyncSession) -> PatientOut:
    """Build PatientOut with resolved nurse name."""
    data = PatientOut.model_validate(patient)
    if patient.responsible_user_id:
        nurse = await db.get(User, patient.responsible_user_id)
        if nurse:
            data.responsible_nurse_name = f"{nurse.first_name} {nurse.last_name}"
    return data


@router.get("", response_model=list[PatientOut])
async def list_patients(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Patient).offset(skip).limit(limit)
    roles = current_user.roles or []
    if "view_all_cases" not in roles and "view_cases" in roles:
        query = query.where(
            (Patient.responsible_user_id == None) | (Patient.responsible_user_id == current_user.user_id)  # noqa: E711
        )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
async def create_patient(
    body: PatientCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("add_case")),
):
    existing = await db.get(Patient, body.hn)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="HN already exists")
    patient = Patient(**body.model_dump(), line_reg_code=secrets.token_hex(3))
    db.add(patient)
    await db.flush()
    await _ensure_tokens_for_patient(patient, db)
    await audit(db, "create", "patient", patient.hn, user_id=current_user.user_id, request=request)
    await db.commit()
    await db.refresh(patient)

    if body.responsible_user_id:
        nurse = await db.get(User, body.responsible_user_id)
        if nurse and nurse.email:
            await send_new_case_email(
                to_email=nurse.email,
                nurse_name=f"{nurse.first_name} {nurse.last_name}",
                patient_name=f"{patient.first_name} {patient.last_name}",
                patient_hn=patient.hn,
                procedures=patient.procedures,
                frontend_url=settings.FRONTEND_URL,
            )

    return patient


@router.get("/{hn}", response_model=PatientOut)
async def get_patient(
    hn: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = await db.get(Patient, hn)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    await audit(db, "view", "patient", hn, user_id=current_user.user_id, request=request)
    await db.commit()
    return await _patient_out(patient, db)


@router.patch("/{hn}", response_model=PatientOut)
async def update_patient(
    hn: str,
    body: PatientUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("edit_case")),
):
    patient = await db.get(Patient, hn)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    updates = body.model_dump(exclude_none=True)
    non_status_updates = {k: v for k, v in updates.items() if k != 'status'}
    if patient.line_user_id and non_status_updates:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ไม่สามารถแก้ไขข้อมูลได้หลังจากเชื่อม LINE แล้ว",
        )
    # Auto-fill responsible_person from user when responsible_user_id is provided
    if 'responsible_user_id' in updates:
        nurse = await db.get(User, updates['responsible_user_id'])
        if nurse:
            updates['responsible_person'] = f"{nurse.first_name} {nurse.last_name}"
    for field, value in updates.items():
        setattr(patient, field, value)
    await _ensure_tokens_for_patient(patient, db)
    await audit(db, "update", "patient", hn, user_id=current_user.user_id, request=request, details={"fields": list(updates.keys())})
    await db.commit()
    await db.refresh(patient)
    return await _patient_out(patient, db)


@router.delete("/{hn}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    hn: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = await db.get(Patient, hn)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    await audit(db, "delete", "patient", hn, user_id=current_user.user_id, request=request)
    await db.execute(delete(FormToken).where(FormToken.patient_hn == hn))
    await db.delete(patient)
    await db.commit()



@router.get("/{hn}/form-tokens", response_model=dict[str, dict])
async def get_form_tokens(
    hn: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("send_assessment")),
):
    patient = await db.get(Patient, hn)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    tokens = (await db.execute(
        select(FormToken).where(
            FormToken.patient_hn == hn,
            FormToken.is_used == False,  # noqa: E712
        )
    )).scalars().all()

    frontend_url = settings.FRONTEND_URL.rstrip("/")
    return {
        t.schedule_date: {
            "token": t.token,
            "url": f"{frontend_url}/form/{t.token}",
            "password": t.token[:6],
        }
        for t in tokens
        if t.schedule_date
    }
