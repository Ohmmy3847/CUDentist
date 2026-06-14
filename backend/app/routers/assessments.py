from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, get_db
from app.models.patient import Patient
from app.models.assessment import Assessment, AssessmentResult
from app.models.user import User
from app.schemas.assessment import AssessmentCreate, AssessmentListItem, AssessmentOut, AssessmentResultUpdate
from app.services.assessment_service import call_risk_service
from app.services.line_service import build_patient_result_message, build_qa_message, push_text

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.get("", response_model=list[AssessmentListItem])
async def list_assessments(
    patient_hn: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = (
        select(Assessment, AssessmentResult.overall_risk)
        .outerjoin(AssessmentResult, Assessment.assessment_id == AssessmentResult.assessment_id)
        .offset(skip)
        .limit(limit)
        .order_by(Assessment.submitted_at.desc())
    )
    if patient_hn:
        query = query.where(Assessment.patient_hn == patient_hn)

    rows = (await db.execute(query)).all()
    items = []
    for assessment, overall_risk in rows:
        items.append(
            AssessmentListItem(
                assessment_id=assessment.assessment_id,
                patient_hn=assessment.patient_hn,
                submitted_at=assessment.submitted_at,
                overall_risk=overall_risk,
                language=assessment.language,
            )
        )
    return items


@router.post("", response_model=AssessmentOut, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    body: AssessmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assessment = Assessment(
        patient_hn=body.patient_hn,
        created_by=current_user.user_id,
        symptom_values=body.symptom_values,
        custom_symptoms=body.custom_symptoms,
        additional_questions=body.additional_questions,
        language=body.language,
    )
    if body.submitted_at:
        assessment.submitted_at = body.submitted_at

    # Remove matching schedule after every assessment creation
    from datetime import timezone
    effective_dt = body.submitted_at or assessment.submitted_at
    target_date_str = effective_dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
    patient = await db.get(Patient, body.patient_hn)
    if patient:
        changed = False
        if patient.follow_up_schedules:
            new_schedules = [d for d in patient.follow_up_schedules if not d.startswith(target_date_str)]
            if len(new_schedules) != len(patient.follow_up_schedules):
                patient.follow_up_schedules = new_schedules
                changed = True
        if patient.follow_up_date:
            fd_str = patient.follow_up_date.astimezone(timezone.utc).strftime("%Y-%m-%d")
            if fd_str == target_date_str:
                patient.follow_up_date = None
                changed = True
        if changed:
            db.add(patient)

    db.add(assessment)
    await db.flush()

    basic_info = dict(body.basic_info or {})
    patient_note = (patient.extra_info or {}).get("note") if patient and patient.extra_info else None
    if patient_note:
        basic_info["patient_note"] = patient_note

    assessment_data = dict(body.symptom_values or {})

    # Set custom_symptoms on assessment (for needs_review_custom tracking)
    # Keep original {symptom, detail} objects in assessment_data — flow_parser handles them
    raw_custom = assessment_data.get("other_symptoms_custom", [])
    if raw_custom and isinstance(raw_custom, list) and not assessment.custom_symptoms:
        assessment.custom_symptoms = [i for i in raw_custom if i]

    risk_payload = {
        "basic_info": basic_info,
        "assessment_data": assessment_data,
        "language": body.language,
        "patient_question": body.additional_questions or "",
    }

    try:
        risk_result = await call_risk_service(risk_payload)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Risk service error: {exc}")

    summary = risk_result.get("summary", {})
    needs_review_question = bool(assessment.additional_questions)
    needs_review_custom = bool(assessment.custom_symptoms)
    # conflict heuristic (same as public flow): check note vs summary
    note = (patient.extra_info or {}).get("note") if patient and patient.extra_info else ""
    note_text = str(note or "")
    summary_text = str(summary.get("summary") or "")
    needs_review_conflict = ("แพ้นม" in note_text or "milk allergy" in note_text.lower()) and (
        "นม" in summary_text or "milk" in summary_text.lower()
    )
    needs_review = needs_review_question or needs_review_custom or needs_review_conflict
    result = AssessmentResult(
        assessment_id=assessment.assessment_id,
        overall_risk=summary.get("overall_risk"),
        flow_results=risk_result.get("flows"),
        clinical_summary=summary.get("summary"),
        qa_answer=risk_result.get("qa_answer"),
        qa_chunks=risk_result.get("qa_chunks"),
        needs_review=needs_review,
        needs_review_question=needs_review_question,
        needs_review_custom=needs_review_custom,
        needs_review_conflict=needs_review_conflict,
    )
    db.add(result)
    await db.commit()

    await db.refresh(assessment)
    await db.refresh(result)
    assessment.result = result
    return assessment


@router.get("/{assessment_id}", response_model=AssessmentOut)
async def get_assessment(
    assessment_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Assessment)
        .options(selectinload(Assessment.result))
        .where(Assessment.assessment_id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return assessment


@router.patch("/{assessment_id}/result", response_model=AssessmentOut)
async def update_assessment_result(
    assessment_id: int,
    body: AssessmentResultUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = await db.execute(
        select(Assessment)
        .options(selectinload(Assessment.result))
        .where(Assessment.assessment_id == assessment_id)
    )
    assessment = q.scalar_one_or_none()
    if not assessment or not assessment.result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    result = assessment.result
    prev_needs_review = bool(result.needs_review)
    if body.clinical_summary is not None:
        result.clinical_summary = body.clinical_summary
    if body.qa_answer_text is not None and result.qa_answer:
        result.qa_answer = {**result.qa_answer, "answer": body.qa_answer_text}
    if body.needs_review is not None:
        result.needs_review = body.needs_review
        if not body.needs_review:
            result.reviewed_by = current_user.user_id

    # granular confirmations (independent)
    if body.confirm_question:
        result.needs_review_question = False
    if body.confirm_custom:
        result.needs_review_custom = False
    if body.confirm_conflict:
        result.needs_review_conflict = False

    # keep aggregate consistent if any flag still requires review
    result.needs_review = bool(result.needs_review_question or result.needs_review_custom or result.needs_review_conflict)

    await db.commit()
    # When all confirmations are cleared (or needs_review toggled to false), send to patient (once).
    if (prev_needs_review and not result.needs_review) and result.patient_notified_at is None:
        patient = await db.get(Patient, assessment.patient_hn)
        if patient and patient.line_user_id:
            # Message 1: recommendation
            await push_text(
                patient.line_user_id,
                build_patient_result_message(
                    assessment.language,
                    result.overall_risk,
                    result.clinical_summary,
                ),
            )
            # Message 2: QA (if patient asked a question)
            if result.qa_answer:
                question = assessment.additional_questions or ""
                qa_text = (result.qa_answer.get("answer") or "").strip()
                if qa_text:
                    await push_text(
                        patient.line_user_id,
                        build_qa_message(assessment.language, question, qa_text),
                    )
            result.patient_notified_at = datetime.now(timezone.utc)
            db.add(result)
            await db.commit()

    await db.refresh(assessment)
    await db.refresh(result)
    assessment.result = result
    return assessment
