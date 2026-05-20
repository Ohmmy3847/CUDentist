from fastapi import APIRouter, Depends
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.assessment import Assessment, AssessmentResult
from app.models.patient import Patient
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _patient_scope(query, user: User):
    roles = user.roles or []
    if "view_all_cases" in roles:
        return query  # sees everything
    if "view_cases" in roles:
        query = query.where(
            or_(Patient.responsible_user_id == None, Patient.responsible_user_id == user.user_id)  # noqa: E711
        )
    return query


@router.get("/stats")
async def get_stats(
    status_filter: str = "active",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base = select(func.count()).select_from(Patient).where(Patient.status == status_filter)
    base = _patient_scope(base, current_user)
    total_patients = (await db.execute(base)).scalar()

    assess_q = (
        select(func.count())
        .select_from(Assessment)
        .join(Patient)
        .where(Patient.status == status_filter)
    )
    assess_q = _patient_scope(assess_q, current_user)
    total_assessments = (await db.execute(assess_q)).scalar()

    risk_q = (
        select(AssessmentResult.overall_risk, func.count())
        .select_from(AssessmentResult)
        .join(Assessment, Assessment.assessment_id == AssessmentResult.assessment_id)
        .join(Patient, Patient.hn == Assessment.patient_hn)
        .where(Patient.status == status_filter)
        .group_by(AssessmentResult.overall_risk)
    )
    risk_q = _patient_scope(risk_q, current_user)
    risk_counts = {row[0]: row[1] for row in (await db.execute(risk_q)).all()}

    return {
        "total_patients": total_patients,
        "total_assessments": total_assessments,
        "risk_counts": risk_counts,
    }


@router.get("/patients")
async def dashboard_patients(
    risk: str | None = None,
    search: str | None = None,
    status: str = "active",
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    latest_result = (
        select(Assessment.patient_hn, func.max(Assessment.assessment_id).label("max_id"))
        .group_by(Assessment.patient_hn)
        .subquery()
    )

    query = (
        select(Patient, AssessmentResult.overall_risk, Assessment.submitted_at, Assessment.assessment_id, AssessmentResult.needs_review)
        .join(latest_result, Patient.hn == latest_result.c.patient_hn, isouter=True)
        .outerjoin(Assessment, Assessment.assessment_id == latest_result.c.max_id)
        .outerjoin(AssessmentResult, AssessmentResult.assessment_id == latest_result.c.max_id)
        .where(Patient.status == status)
        .order_by(Assessment.submitted_at.desc().nullslast())
    )

    query = _patient_scope(query, current_user)

    if search:
        query = query.where(
            Patient.hn.ilike(f"%{search}%")
            | Patient.first_name.ilike(f"%{search}%")
            | Patient.last_name.ilike(f"%{search}%")
            | Patient.phone.ilike(f"%{search}%")
        )
    if risk:
        query = query.where(AssessmentResult.overall_risk == risk)

    count_q = select(func.count()).select_from(query.subquery())
    total_count = (await db.execute(count_q)).scalar() or 0

    rows = (await db.execute(query.offset(skip).limit(limit))).all()

    return {
        "total": total_count,
        "patients": [
            {
                "hn": patient.hn,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "phone": patient.phone,
                "procedures": patient.procedures,
                "overall_risk": overall_risk,
                "last_assessment_at": submitted_at,
                "last_assessment_id": assessment_id,
                "follow_up_schedules": patient.follow_up_schedules or [],
                "needs_review": bool(needs_review),
                "line_user_id": patient.line_user_id,
                "line_reg_code": patient.line_reg_code,
            }
            for patient, overall_risk, submitted_at, assessment_id, needs_review in rows
        ],
    }
