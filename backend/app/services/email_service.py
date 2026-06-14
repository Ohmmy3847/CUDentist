import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import partial

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def _send_via_resend(to_email: str, subject: str, body_html: str) -> None:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
            json={"from": settings.SMTP_FROM, "to": [to_email], "subject": subject, "html": body_html},
        )
        resp.raise_for_status()


def _send_sync(to_email: str, subject: str, body_html: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    # Port 465 = SSL from the start (SMTP_SSL), port 587 = STARTTLS upgrade
    if settings.SMTP_PORT == 465:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.sendmail(settings.SMTP_FROM, to_email, msg.as_string())
    else:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            if settings.SMTP_TLS:
                smtp.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.sendmail(settings.SMTP_FROM, to_email, msg.as_string())


async def send_email(to_email: str, subject: str, body_html: str) -> None:
    # Prefer Resend (HTTP API) over SMTP — Railway blocks outbound SMTP
    if settings.RESEND_API_KEY:
        try:
            await _send_via_resend(to_email, subject, body_html)
            logger.info(f"Email sent via Resend to {to_email}: {subject}")
        except Exception as exc:
            logger.error(f"Resend failed to {to_email}: {exc}")
        return

    if not settings.SMTP_HOST:
        logger.warning(f"No email provider configured. Would send to {to_email}: {subject}")
        return
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, partial(_send_sync, to_email, subject, body_html))
        logger.info(f"Email sent via SMTP to {to_email}: {subject}")
    except Exception as exc:
        logger.error(f"SMTP failed to {to_email}: {exc}")


async def send_welcome_email(to_email: str, full_name: str, username: str, temp_password: str) -> None:
    subject = "ข้อมูลบัญชีผู้ใช้งานระบบติดตามอาการผู้ป่วย"
    body = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: auto;">
      <h2>ยินดีต้อนรับ {full_name}</h2>
      <p>บัญชีผู้ใช้งานของคุณถูกสร้างแล้ว กรุณาเข้าสู่ระบบด้วยข้อมูลต่อไปนี้:</p>
      <table style="border-collapse: collapse; width: 100%;">
        <tr><td style="padding: 6px; font-weight: bold;">ชื่อผู้ใช้:</td><td style="padding: 6px;">{username}</td></tr>
        <tr><td style="padding: 6px; font-weight: bold;">รหัสผ่าน:</td><td style="padding: 6px;">{temp_password}</td></tr>
      </table>
      <p style="margin-top: 16px;">
        <a href="{settings.FRONTEND_URL}/login" style="background: #2563eb; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none;">
          เข้าสู่ระบบ
        </a>
      </p>
      <p style="color: #6b7280; font-size: 12px; margin-top: 16px;">กรุณาเปลี่ยนรหัสผ่านหลังจากเข้าสู่ระบบครั้งแรก</p>
    </div>
    """
    await send_email(to_email, subject, body)


async def send_otp_email(to_email: str, full_name: str, code: str, purpose: str) -> None:
    purpose_text = {"login": "เข้าสู่ระบบ", "change_password": "เปลี่ยนรหัสผ่าน", "change_email": "เปลี่ยนอีเมล"}.get(purpose, purpose)
    subject = f"รหัส OTP สำหรับ{purpose_text} — ระบบติดตามอาการผู้ป่วย"
    body = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: auto;">
      <h2 style="color: #1f2937;">รหัสยืนยันตัวตน (OTP)</h2>
      <p>สวัสดี {full_name},</p>
      <p>รหัส OTP สำหรับ<strong>{purpose_text}</strong>ของคุณคือ:</p>
      <div style="font-size: 40px; font-weight: bold; letter-spacing: 10px; text-align: center;
                  padding: 24px; background: #f3f4f6; border-radius: 12px; margin: 20px 0;
                  color: #1d4ed8; font-family: monospace;">
        {code}
      </div>
      <p style="color: #6b7280;">รหัสนี้มีอายุ <strong>5 นาที</strong> ใช้ได้เพียงครั้งเดียว</p>
      <p style="color: #9ca3af; font-size: 12px; margin-top: 16px;">หากไม่ได้ดำเนินการนี้ กรุณาเพิกเฉยอีเมลนี้</p>
    </div>
    """
    await send_email(to_email, subject, body)


_ROLE_LABEL: dict[str, str] = {
    'send_assessment': 'ส่งแบบประเมิน',
    'view_cases': 'ดูเคสที่รับผิดชอบ',
    'view_all_cases': 'ดูเคสทั้งหมด',
    'add_case': 'เพิ่มเคสใหม่',
    'edit_case': 'แก้ไขข้อมูลเคส',
    'manage_users': 'จัดการบัญชีผู้ใช้',
    'manage_docs': 'จัดการเอกสาร',
}


async def send_permission_change_email(
    to_email: str,
    full_name: str,
    old_roles: list[str],
    new_roles: list[str],
    changed_by: str,
) -> None:
    subject = "การเปลี่ยนแปลงสิทธิ์ใช้งาน — ระบบติดตามอาการผู้ป่วย"
    old_text = ', '.join(_ROLE_LABEL.get(r, r) for r in old_roles) or '—'
    new_text = ', '.join(_ROLE_LABEL.get(r, r) for r in new_roles) or '—'
    body = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: auto;">
      <h2 style="color: #1f2937;">การเปลี่ยนแปลงสิทธิ์ใช้งาน</h2>
      <p>สวัสดี {full_name},</p>
      <p>สิทธิ์การใช้งานของคุณในระบบได้รับการเปลี่ยนแปลงโดย <strong>{changed_by}</strong></p>
      <table style="border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 14px;">
        <tr>
          <td style="padding: 10px 12px; font-weight: bold; background: #f9fafb; border: 1px solid #e5e7eb; width: 120px;">สิทธิ์เดิม</td>
          <td style="padding: 10px 12px; border: 1px solid #e5e7eb;">{old_text}</td>
        </tr>
        <tr>
          <td style="padding: 10px 12px; font-weight: bold; background: #f9fafb; border: 1px solid #e5e7eb;">สิทธิ์ใหม่</td>
          <td style="padding: 10px 12px; border: 1px solid #e5e7eb;">{new_text}</td>
        </tr>
      </table>
      <p style="color: #6b7280; font-size: 13px;">หากไม่ได้รับทราบการเปลี่ยนแปลงนี้ กรุณาติดต่อผู้ดูแลระบบ</p>
    </div>
    """
    await send_email(to_email, subject, body)


async def send_patient_response_email(
    to_email: str,
    nurse_name: str,
    patient_name: str,
    patient_hn: str,
    overall_risk: str,
    frontend_url: str,
    needs_review: bool = False,
    clinical_summary: str | None = None,
    qa_answer: str | None = None,
) -> None:
    risk_map = {'low': ('ต่ำ', '#16a34a', '#dcfce7'), 'medium': ('กลาง', '#d97706', '#fef9c3'), 'high': ('สูง', '#dc2626', '#fee2e2')}
    risk_label, risk_color, risk_bg = risk_map.get(overall_risk, ('ไม่ระบุ', '#6b7280', '#f9fafb'))

    review_notice = ''
    if needs_review:
        review_notice = '''
        <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:12px 16px;margin:16px 0;">
          <p style="margin:0;color:#92400e;font-weight:bold;font-size:14px;">⚠️ เคสนี้ต้องการการตรวจสอบจากเจ้าหน้าที่</p>
          <p style="margin:6px 0 0;color:#b45309;font-size:13px;">ผู้ป่วยมีอาการพิเศษหรือคำถามเพิ่มเติมที่ต้องการการประเมินจากบุคลากรทางการแพทย์</p>
        </div>'''

    summary_section = ''
    if clinical_summary:
        lines = [f'<li style="margin-bottom:6px;">{line.lstrip("•-– ").strip()}</li>'
                 for line in clinical_summary.split('\n') if line.strip()]
        summary_section = f'''
        <div style="margin-top:20px;">
          <p style="margin:0 0 8px;font-weight:bold;color:#1f2937;font-size:14px;">คำแนะนำจากระบบ</p>
          <ul style="margin:0;padding-left:20px;color:#374151;font-size:14px;line-height:1.7;">
            {''.join(lines)}
          </ul>
        </div>'''

    qa_section = ''
    if qa_answer:
        qa_section = f'''
        <div style="margin-top:16px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;">
          <p style="margin:0 0 6px;font-weight:bold;color:#1f2937;font-size:14px;">คำตอบสำหรับคำถามเพิ่มเติม</p>
          <p style="margin:0;color:#374151;font-size:14px;line-height:1.7;">{qa_answer}</p>
        </div>'''

    subject = f"[{'ต้องตรวจสอบ' if needs_review else 'แบบประเมิน'}] {patient_name} (HN: {patient_hn}) — ระดับความเสี่ยง: {risk_label}"
    body = f"""
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 560px; margin: auto; color: #1f2937;">
      <div style="background: #2563eb; padding: 20px 24px; border-radius: 10px 10px 0 0;">
        <h2 style="margin: 0; color: white; font-size: 18px;">ผู้ป่วยส่งแบบประเมินแล้ว</h2>
      </div>
      <div style="background: white; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 10px 10px; padding: 24px;">
        <p style="margin: 0 0 16px;">สวัสดี <strong>{nurse_name}</strong>,</p>
        <p style="margin: 0 0 16px; color: #4b5563; font-size: 14px;">ผู้ป่วยในความรับผิดชอบของคุณได้ส่งแบบประเมินอาการเรียบร้อยแล้ว</p>

        <table style="border-collapse: collapse; width: 100%; font-size: 14px; border-radius: 8px; overflow: hidden; border: 1px solid #e5e7eb;">
          <tr>
            <td style="padding: 10px 14px; font-weight: 600; background: #f9fafb; border-bottom: 1px solid #e5e7eb; width: 130px; color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: .05em;">ชื่อผู้ป่วย</td>
            <td style="padding: 10px 14px; border-bottom: 1px solid #e5e7eb; font-weight: 500;">{patient_name}</td>
          </tr>
          <tr>
            <td style="padding: 10px 14px; font-weight: 600; background: #f9fafb; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: .05em;">HN</td>
            <td style="padding: 10px 14px; border-bottom: 1px solid #e5e7eb; font-family: monospace; font-size: 15px;">{patient_hn}</td>
          </tr>
          <tr>
            <td style="padding: 10px 14px; font-weight: 600; background: #f9fafb; color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: .05em;">ระดับความเสี่ยง</td>
            <td style="padding: 10px 14px;">
              <span style="background: {risk_bg}; color: {risk_color}; padding: 3px 12px; border-radius: 999px; font-weight: 700; font-size: 13px;">{risk_label}</span>
            </td>
          </tr>
        </table>

        {review_notice}
        {summary_section}
        {qa_section}

        <div style="margin-top: 24px; padding-top: 20px; border-top: 1px solid #f3f4f6;">
          <a href="{frontend_url}/patients/{patient_hn}" style="display: inline-block; background: #2563eb; color: white; padding: 11px 22px; border-radius: 7px; text-decoration: none; font-size: 14px; font-weight: 500;">
            ดูรายละเอียดเคส →
          </a>
        </div>
        <p style="margin: 16px 0 0; color: #9ca3af; font-size: 12px;">อีเมลนี้ส่งจากระบบติดตามอาการผู้ป่วยหลังผ่าตัดทันตกรรม</p>
      </div>
    </div>
    """
    await send_email(to_email, subject, body)


async def send_new_case_email(
    to_email: str,
    nurse_name: str,
    patient_name: str,
    patient_hn: str,
    procedures: list | None,
    frontend_url: str,
) -> None:
    proc_text = ""
    if procedures:
        items = "".join(
            f'<li style="margin-bottom:4px;">{p.get("name", p) if isinstance(p, dict) else p}</li>'
            for p in procedures
        )
        proc_text = f'<ul style="margin:8px 0 0;padding-left:20px;color:#374151;font-size:14px;line-height:1.7;">{items}</ul>'

    subject = f"[เคสใหม่] {patient_name} (HN: {patient_hn}) — ระบบติดตามอาการผู้ป่วย"
    body = f"""
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 560px; margin: auto; color: #1f2937;">
      <div style="background: #2563eb; padding: 20px 24px; border-radius: 10px 10px 0 0;">
        <h2 style="margin: 0; color: white; font-size: 18px;">มีเคสใหม่ในความรับผิดชอบของคุณ</h2>
      </div>
      <div style="background: white; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 10px 10px; padding: 24px;">
        <p style="margin: 0 0 16px;">สวัสดี <strong>{nurse_name}</strong>,</p>
        <p style="margin: 0 0 16px; color: #4b5563; font-size: 14px;">เคสผู้ป่วยใหม่ได้รับการมอบหมายให้อยู่ในความรับผิดชอบของคุณแล้ว</p>

        <table style="border-collapse: collapse; width: 100%; font-size: 14px; border-radius: 8px; overflow: hidden; border: 1px solid #e5e7eb;">
          <tr>
            <td style="padding: 10px 14px; font-weight: 600; background: #f9fafb; border-bottom: 1px solid #e5e7eb; width: 130px; color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: .05em;">ชื่อผู้ป่วย</td>
            <td style="padding: 10px 14px; border-bottom: 1px solid #e5e7eb; font-weight: 500;">{patient_name}</td>
          </tr>
          <tr>
            <td style="padding: 10px 14px; font-weight: 600; background: #f9fafb; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: .05em;">HN</td>
            <td style="padding: 10px 14px; border-bottom: 1px solid #e5e7eb; font-family: monospace; font-size: 15px;">{patient_hn}</td>
          </tr>
          <tr>
            <td style="padding: 10px 14px; font-weight: 600; background: #f9fafb; color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: .05em;">หัตถการ</td>
            <td style="padding: 10px 14px;">{proc_text or '<span style="color:#9ca3af;">—</span>'}</td>
          </tr>
        </table>

        <div style="margin-top: 24px; padding-top: 20px; border-top: 1px solid #f3f4f6;">
          <a href="{frontend_url}/patients/{patient_hn}" style="display: inline-block; background: #2563eb; color: white; padding: 11px 22px; border-radius: 7px; text-decoration: none; font-size: 14px; font-weight: 500;">
            ดูข้อมูลเคส →
          </a>
        </div>
        <p style="margin: 16px 0 0; color: #9ca3af; font-size: 12px;">อีเมลนี้ส่งจากระบบติดตามอาการผู้ป่วยหลังผ่าตัดทันตกรรม</p>
      </div>
    </div>
    """
    await send_email(to_email, subject, body)


async def send_reset_password_email(to_email: str, full_name: str, reset_token: str) -> None:
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    subject = "รีเซ็ตรหัสผ่าน — ระบบติดตามอาการผู้ป่วย"
    body = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: auto;">
      <h2>รีเซ็ตรหัสผ่าน</h2>
      <p>สวัสดี {full_name},</p>
      <p>คลิกปุ่มด้านล่างเพื่อตั้งรหัสผ่านใหม่ ลิงก์มีอายุ 1 ชั่วโมง</p>
      <p style="margin-top: 16px;">
        <a href="{reset_url}" style="background: #2563eb; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none;">
          ตั้งรหัสผ่านใหม่
        </a>
      </p>
      <p style="color: #6b7280; font-size: 12px; margin-top: 16px;">หากไม่ได้ขอรีเซ็ตรหัสผ่าน กรุณาเพิกเฉยอีเมลนี้</p>
    </div>
    """
    await send_email(to_email, subject, body)
