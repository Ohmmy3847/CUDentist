import base64
import hashlib
import hmac
import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"
_LINE_PROFILE_URL = "https://api.line.me/v2/bot/profile"

_TH_MONTHS = [
    "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
    "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค.",
]


def verify_signature(body: bytes, signature: str) -> bool:
    if not settings.LINE_CHANNEL_SECRET:
        return False
    mac = hmac.new(
        settings.LINE_CHANNEL_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).digest()
    expected = base64.b64encode(mac).decode("utf-8")
    return hmac.compare_digest(expected, signature)


async def push_text(user_id: str, text: str) -> None:
    if not settings.LINE_CHANNEL_ACCESS_TOKEN:
        logger.warning("LINE not configured — skipping push to %s: %s", user_id, text[:60])
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                _LINE_PUSH_URL,
                headers={"Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}"},
                json={"to": user_id, "messages": [{"type": "text", "text": text}]},
            )
            resp.raise_for_status()
            logger.info("LINE push sent to %s", user_id)
    except Exception as exc:
        logger.error("LINE push failed to %s: %s", user_id, exc)


async def push_form_link(
    user_id: str,
    patient_name: str,
    url: str,
    password: str,
) -> None:
    text = (
        f"สวัสดีคุณ{patient_name} 👋\n\n"
        f"ถึงเวลาประเมินอาการหลังผ่าตัดแล้วค่ะ\n\n"
        f"📋 กรอกแบบประเมินได้ที่:\n{url}\n\n"
        f"🔑 รหัสผ่าน: {password}\n\n"
        "กรุณากรอกให้ครบก่อนลิงก์หมดอายุนะคะ 🙏"
    )
    await push_text(user_id, text)


async def fetch_line_profile(user_id: str) -> dict | None:
    if not settings.LINE_CHANNEL_ACCESS_TOKEN:
        return None

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{_LINE_PROFILE_URL}/{user_id}",
                headers={"Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}"},
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:
        logger.error("LINE profile fetch failed for %s: %s", user_id, exc)
        return None


def build_qa_message(language: str | None, question: str, answer: str) -> str:
    question = (question or "").strip()[:300]
    answer = (answer or "").strip()[:600]
    if (language or "th") == "en":
        return f"— Answer to your question —\n\nQ: {question}\n\nA: {answer}"
    return f"— คำตอบสำหรับคำถามของคุณ —\n\nคำถาม: {question}\n\nคำตอบ: {answer}"


def build_patient_result_message(
    language: str | None,
    overall_risk: str | None,
    clinical_summary: str | None,
    qa_answer: str | None = None,
) -> str:
    overall_risk = overall_risk or "-"
    clinical_summary = (clinical_summary or "").strip()[:800]
    qa_answer = (qa_answer or "").strip()[:600]

    if (language or "th") == "en":
        msg = f"Your assessment has been processed.\n\nRisk level: {overall_risk}"
        if clinical_summary:
            msg += f"\n\n{clinical_summary}"
        if qa_answer:
            msg += f"\n\n— Answer to your question —\n{qa_answer}"
        return msg

    msg = f"ระบบประมวลผลแบบประเมินของคุณเรียบร้อยแล้วค่ะ\n\nระดับความเสี่ยง: {overall_risk}"
    if clinical_summary:
        msg += f"\n\n{clinical_summary}"
    if qa_answer:
        msg += f"\n\n— คำตอบสำหรับคำถามของคุณ —\n{qa_answer}"
    return msg


def format_schedules_th(schedules: list) -> str:
    lines = []
    for i, s in enumerate(sorted(schedules), 1):
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            ict = dt + timedelta(hours=7)
            month = _TH_MONTHS[ict.month - 1]
            lines.append(f"  {i}. {ict.day} {month} {ict.year + 543} เวลา {ict.strftime('%H:%M')} น.")
        except Exception:
            lines.append(f"  {i}. {s}")
    return "\n".join(lines) if lines else "  (ไม่มีตารางนัด)"
