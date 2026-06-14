import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_db
from app.models.assessment import Assessment, AssessmentResult
from app.models.consent_record import ConsentRecord
from app.models.form_token import FormToken
from app.models.patient import Patient
from app.models.user import User
from app.schemas.public_form import PublicAssessmentSubmit, PublicPatientInfo
from app.services.assessment_service import call_risk_service
from app.services.audit_service import audit
from app.services.email_service import send_patient_response_email
from app.services.line_service import build_patient_result_message, push_text

router = APIRouter(prefix="/public", tags=["public"])


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


async def _get_valid_token(token: str, db: AsyncSession) -> tuple[FormToken, Patient]:
    row = await db.get(FormToken, token)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ลิงก์ไม่ถูกต้อง")
    if row.is_used:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="แบบประเมินนี้ถูกส่งไปแล้ว")

    # Block early submission: allow only from 2 hours before schedule (Thailand = UTC+7)
    if row.schedule_date:
        try:
            from dateutil.parser import isoparse
            THAI_TZ = timezone(timedelta(hours=7))
            sched = isoparse(row.schedule_date.replace("Z", "+00:00"))
            if sched.tzinfo is None:
                # Naive string → assume Thai local time (UTC+7), not UTC
                sched = sched.replace(tzinfo=THAI_TZ)
            now = datetime.now(timezone.utc)
            earliest = sched - timedelta(hours=2)
            if now < earliest:
                sched_th = sched.astimezone(THAI_TZ)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"ยังไม่ถึงเวลาประเมิน กรุณารอจนถึงวันที่ {sched_th.strftime('%d/%m/%Y เวลา %H:%M')} น."
                )
        except HTTPException:
            raise
        except Exception:
            pass

    patient = await db.get(Patient, row.patient_hn)
    if not patient or patient.status != "active":
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="เคสนี้ถูกปิดไปแล้ว ไม่สามารถประเมินได้")
        
    return row, patient


def _verify_password(row: FormToken, password: str) -> None:
    if not row.password_hash or _hash(password) != row.password_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="รหัสผ่านไม่ถูกต้อง")


@router.get("/form/{token}")
async def check_token(token: str, db: AsyncSession = Depends(get_db)):
    """Validate token is real and not expired — returns no patient data."""
    await _get_valid_token(token, db)
    return {"valid": True}


@router.post("/form/{token}/unlock", response_model=PublicPatientInfo)
async def unlock_form(token: str, body: dict, db: AsyncSession = Depends(get_db)):
    """Verify password and return patient display info."""
    password = body.get("password", "")
    row, patient = await _get_valid_token(token, db)
    _verify_password(row, password)

    extra = patient.extra_info or {}
    return PublicPatientInfo(
        first_name=patient.first_name,
        last_name=patient.last_name,
        gender=patient.gender,
        date_of_birth=patient.date_of_birth,
        phone=patient.phone,
        procedures=patient.procedures,
        schedule_date=row.schedule_date,
        surgery_date=extra.get("surgery_date"),
        discharge_date=extra.get("discharge_date"),
        note=extra.get("note"),
    )


async def process_risk_and_save(session_factory, assessment_id: int, risk_payload: dict, has_custom_symptoms: bool = False):
    async with session_factory() as db:
        try:
            risk_result = await call_risk_service(risk_payload)
            summary = risk_result.get("summary", {})
            has_patient_question = bool((risk_payload.get("patient_question") or "").strip())
            # Simple conflict heuristic: if note indicates milk allergy and summary recommends milk.
            assessment = await db.get(Assessment, assessment_id)
            patient = await db.get(Patient, assessment.patient_hn) if assessment else None
            note = (patient.extra_info or {}).get("note") if patient and patient.extra_info else ""
            note_text = str(note or "")
            summary_text = str(summary.get("summary") or "")
            needs_review_conflict = ("แพ้นม" in note_text or "milk allergy" in note_text.lower()) and (
                "นม" in summary_text or "milk" in summary_text.lower()
            )
            result = AssessmentResult(
                assessment_id=assessment_id,
                overall_risk=summary.get("overall_risk"),
                flow_results=risk_result.get("flows"),
                clinical_summary=summary.get("summary"),
                qa_answer=risk_result.get("qa_answer"),
                qa_chunks=risk_result.get("qa_chunks"),
                needs_review_question=has_patient_question,
                needs_review_custom=has_custom_symptoms,
                needs_review_conflict=needs_review_conflict,
                needs_review=has_custom_symptoms or has_patient_question or needs_review_conflict,
            )
            db.add(result)
            await db.commit()

            assessment = assessment
            patient = patient
            # Send to patient only when it does NOT require staff confirmation:
            # 1) has patient additional question -> needs confirmation
            # 2) has other/custom symptoms -> needs confirmation
            if patient and patient.line_user_id and not (has_patient_question or has_custom_symptoms or needs_review_conflict):
                text = build_patient_result_message(
                    assessment.language if assessment else "th",
                    summary.get("overall_risk"),
                    summary.get("summary"),
                )
                await push_text(patient.line_user_id, text)
                result.patient_notified_at = datetime.now(timezone.utc)
                db.add(result)
                await db.commit()
            # Email responsible nurse
            if patient and patient.responsible_user_id:
                from sqlalchemy import select as sa_select
                nurse_res = await db.execute(sa_select(User).where(User.user_id == patient.responsible_user_id))
                nurse = nurse_res.scalar_one_or_none()
                if nurse and nurse.email:
                    patient_name = f"{patient.first_name} {patient.last_name}"
                    qa_data = risk_result.get("qa_answer")
                    qa_text = (qa_data.get("answer") or "").strip() if isinstance(qa_data, dict) else None
                    patient_question = (risk_payload.get("patient_question") or "").strip() or None
                    await send_patient_response_email(
                        to_email=nurse.email,
                        nurse_name=f"{nurse.first_name} {nurse.last_name}",
                        patient_name=patient_name,
                        patient_hn=assessment.patient_hn,
                        overall_risk=summary.get("overall_risk") or "",
                        frontend_url=settings.FRONTEND_URL,
                        needs_review=result.needs_review,
                        clinical_summary=summary.get("summary"),
                        qa_answer=qa_text or None,
                        patient_question=patient_question,
                    )
        except Exception as exc:
            print(f"Background risk processing failed for assessment {assessment_id}: {exc}")


@router.post("/form/{token}/submit", status_code=status.HTTP_201_CREATED)
async def submit_public_form(
    token: str,
    body: PublicAssessmentSubmit,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Re-verify password then create assessment."""
    row, patient = await _get_valid_token(token, db)
    _verify_password(row, body.password)

    assessment = Assessment(
        patient_hn=row.patient_hn,
        created_by=None,
        symptom_values=body.symptom_values,
        custom_symptoms=body.custom_symptoms,
        additional_questions=body.additional_questions,
        language=body.language,
    )
    if body.submitted_at:
        assessment.submitted_at = body.submitted_at
    elif row.schedule_date:
        # Use schedule date as submitted_at if no custom date is provided
        from dateutil.parser import isoparse
        assessment.submitted_at = isoparse(row.schedule_date)

    db.add(assessment)
    row.is_used = True
    db.add(row)

    # PDPA: record patient consent at time of form submission
    consent = ConsentRecord(
        patient_hn=row.patient_hn,
        method="public_form",
        form_token=token,
        ip_address=request.client.host if request.client else None,
    )
    db.add(consent)
    await audit(db, "submit", "assessment", row.patient_hn, user_id=None, request=request)
    
    # Remove matching schedule from patient after form submission
    from datetime import timezone
    effective_dt = assessment.submitted_at
    target_date_str = effective_dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
    patient = await db.get(Patient, row.patient_hn)
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

    await db.commit()
    await db.refresh(assessment)

    assessment_data = body.symptom_values or {}
    if body.custom_symptoms:
        assessment_data["other_symptoms_custom"] = body.custom_symptoms

    basic_info = dict(body.basic_info or {})
    patient_note = (patient.extra_info or {}).get("note") if patient and patient.extra_info else None
    if patient_note:
        basic_info["patient_note"] = patient_note

    risk_payload = {
        "basic_info": basic_info,
        "assessment_data": assessment_data,
        "language": body.language,
        "patient_question": body.additional_questions or "",
    }

    background_tasks.add_task(
        process_risk_and_save,
        request.app.state.session_factory,
        assessment.assessment_id,
        risk_payload,
        bool(body.custom_symptoms),
    )

    return {"message": "ส่งแบบประเมินสำเร็จและกำลังประมวลผล", "assessment_id": assessment.assessment_id}
