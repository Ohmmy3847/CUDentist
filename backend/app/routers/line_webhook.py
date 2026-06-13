import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, status, Depends
from sqlalchemy import select

from app.core.deps import require_admin, get_db
from app.models.assessment import Assessment, AssessmentResult
from app.models.patient import Patient
from app.services.line_service import (
    build_patient_result_message,
    fetch_line_profile,
    format_schedules_th,
    push_text,
    verify_signature,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/line", tags=["line"])

_EXPECT_CODE_TTL_SECONDS = 10 * 60
_expecting_code_until: dict[str, float] = {}

_WELCOME = (
    "สวัสดีค่ะ 👋 ยินดีต้อนรับสู่ระบบติดตามอาการหลังผ่าตัดของคลินิก\n\n"
    "พิมพ์รหัส 6 ตัวอักษรที่ได้รับจากพยาบาลเพื่อลงทะเบียน\n"
    "หรือพิมพ์คำว่า register เพื่อดูวิธีลงทะเบียนค่ะ"
)

_REGISTER_HINT = (
    "ลงทะเบียนใช้งาน\n\n"
    "1) กดเมนู “ลงทะเบียน/Registration” (ถ้ามี) หรือพิมพ์ register\n"
    "2) ภายใน 10 นาที ให้พิมพ์รหัส 6 ตัวอักษรที่ได้รับจากพยาบาล เช่น ABC123\n"
)


@router.post("/webhook")
async def line_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Line-Signature", "")

    if not verify_signature(body, signature):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    payload = await request.json()
    session_factory = request.app.state.session_factory

    for event in payload.get("events", []):
        line_user_id = event.get("source", {}).get("userId")
        if not line_user_id:
            continue

        event_type = event.get("type")

        if event_type == "follow":
            await push_text(line_user_id, _WELCOME)

        elif event_type == "postback":
            data = (event.get("postback", {}).get("data") or "").strip().lower()
            if data in {"action=register", "register"}:
                _expecting_code_until[line_user_id] = datetime.now(timezone.utc).timestamp() + _EXPECT_CODE_TTL_SECONDS
                await push_text(line_user_id, _REGISTER_HINT)

        elif event_type == "message" and event.get("message", {}).get("type") == "text":
            text = event["message"]["text"].strip()
            lower = text.lower()
            if ("register" in lower) or ("ลงทะเบียน" in lower):
                _expecting_code_until[line_user_id] = datetime.now(timezone.utc).timestamp() + _EXPECT_CODE_TTL_SECONDS
                await push_text(line_user_id, _REGISTER_HINT)
                continue
            if ("help" in lower) or ("ช่วยเหลือ" in lower) or ("คำถามที่พบบ่อย" in text):
                _expecting_code_until.pop(line_user_id, None)
                await push_text(line_user_id, _WELCOME)
                continue

            if await _handle_registration(session_factory, line_user_id, text):
                continue

            code = text.strip().lower()
            if len(code) == 6 and code.isalnum():
                await push_text(
                    line_user_id,
                    "กรุณากดเมนู “ลงทะเบียน/Registration” หรือพิมพ์ register ก่อนนะคะ แล้วค่อยส่งรหัส 6 ตัวอีกครั้งค่ะ",
                )

    return {"status": "ok"}


async def _handle_registration(session_factory, line_user_id: str, text: str) -> bool:
    now_ts = datetime.now(timezone.utc).timestamp()
    until = _expecting_code_until.get(line_user_id, 0)
    if until < now_ts:
        # Not in registration flow; ignore code-like inputs here.
        return False

    code = text.strip().lower()

    if len(code) != 6 or not code.isalnum():
        await push_text(line_user_id, "กรุณาส่งรหัส 6 ตัวอักษรที่ได้รับจากพยาบาลค่ะ")
        return True

    async with session_factory() as db:
        result = await db.execute(
            select(Patient).where(Patient.line_reg_code == code)
        )
        patient = result.scalar_one_or_none()

        if not patient:
            await push_text(
                line_user_id,
                "ไม่พบรหัสนี้ค่ะ กรุณาตรวจสอบรหัสและลองใหม่อีกครั้ง\nหรือติดต่อพยาบาลเพื่อรับรหัส",
            )
            return True

        if patient.line_user_id and patient.line_user_id != line_user_id:
            await push_text(line_user_id, "รหัสนี้ถูกใช้งานแล้วค่ะ กรุณาติดต่อพยาบาล")
            return True

        already_registered = patient.line_user_id == line_user_id
        if not already_registered:
            patient.line_user_id = line_user_id
            profile = await fetch_line_profile(line_user_id)
            if profile:
                patient.line_display_name = profile.get("displayName") or patient.line_display_name
                patient.line_picture_url = profile.get("pictureUrl") or patient.line_picture_url
            db.add(patient)
            await db.commit()

            # Send any assessment results that were processed before LINE was linked
            pending = await db.execute(
                select(AssessmentResult)
                .join(Assessment, Assessment.assessment_id == AssessmentResult.assessment_id)
                .where(
                    Assessment.patient_hn == patient.hn,
                    AssessmentResult.needs_review == False,  # noqa: E712
                    AssessmentResult.patient_notified_at.is_(None),
                )
            )
            for result in pending.scalars().all():
                assessment_row = await db.get(Assessment, result.assessment_id)
                text = build_patient_result_message(
                    assessment_row.language if assessment_row else "th",
                    result.overall_risk,
                    result.clinical_summary,
                )
                await push_text(line_user_id, text)
                result.patient_notified_at = datetime.now(timezone.utc)
                db.add(result)
            await db.commit()

        schedules = patient.follow_up_schedules or []
        schedule_text = format_schedules_th(schedules)

        header = (
            f"คุณได้ลงทะเบียนไว้แล้วค่ะ คุณ{patient.first_name} {patient.last_name} ✅\n\n"
            if already_registered
            else f"ลงทะเบียนสำเร็จค่ะ คุณ{patient.first_name} {patient.last_name} 🎉\n\n"
        )
        message = (
            f"{header}"
            f"ตารางประเมินอาการของคุณ:\n{schedule_text}\n\n"
            "ระบบจะส่งลิงก์แบบประเมินให้ตามเวลาที่กำหนดค่ะ 📅"
        )

        await push_text(
            line_user_id,
            message,
        )

        _expecting_code_until.pop(line_user_id, None)
        return True


@router.post("/admin/sync-profiles", dependencies=[Depends(require_admin)])
async def sync_line_profiles(limit: int = 50, db=Depends(get_db)):
    """
    Backfill LINE profile fields (displayName/pictureUrl) for already-registered patients.
    Requires manage_users permission.
    """
    result = await db.execute(
        select(Patient).where(
            Patient.line_user_id.isnot(None),
            (Patient.line_display_name.is_(None) | Patient.line_picture_url.is_(None)),
        ).limit(limit)
    )
    patients = result.scalars().all()

    updated = 0
    attempted = 0
    for patient in patients:
        if not patient.line_user_id:
            continue
        attempted += 1
        profile = await fetch_line_profile(patient.line_user_id)
        if not profile:
            continue
        new_name = profile.get("displayName")
        new_pic = profile.get("pictureUrl")
        if new_name and patient.line_display_name != new_name:
            patient.line_display_name = new_name
        if new_pic and patient.line_picture_url != new_pic:
            patient.line_picture_url = new_pic
        db.add(patient)
        updated += 1

    await db.commit()
    return {"attempted": attempted, "updated": updated, "limit": limit}
