import random
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, require_admin
from app.core.security import create_access_token, hash_password, verify_password
from app.models.email_otp import EmailOTP
from app.models.password_reset import PasswordResetToken
from app.models.trusted_device import TrustedDevice
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    ConfirmChangeEmailRequest,
    ConfirmChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    RequestChangeEmailRequest,
    RequestChangePasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserOut,
    UserUpdate,
    VerifyOTPRequest,
)
from pydantic import BaseModel
from app.services.email_service import (
    send_otp_email,
    send_permission_change_email,
    send_reset_password_email,
    send_welcome_email,
)

router = APIRouter(prefix="/auth", tags=["auth"])

OTP_EXPIRE_MINUTES = 5
DEVICE_TRUST_DAYS = 30


def _generate_otp() -> str:
    return ''.join(random.choices('0123456789', k=6))


async def _create_otp(db: AsyncSession, user_id: int, purpose: str, payload: str | None = None) -> EmailOTP:
    otp = EmailOTP(
        session_token=secrets.token_urlsafe(32),
        user_id=user_id,
        code=_generate_otp(),
        purpose=purpose,
        payload=payload,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES),
        created_at=datetime.now(timezone.utc),
    )
    db.add(otp)
    await db.commit()
    await db.refresh(otp)
    return otp


async def _verify_otp(db: AsyncSession, otp_session: str, code: str) -> EmailOTP:
    result = await db.execute(select(EmailOTP).where(EmailOTP.session_token == otp_session))
    otp = result.scalar_one_or_none()
    if not otp or otp.used or otp.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="รหัส OTP ไม่ถูกต้องหรือหมดอายุแล้ว")
    if otp.code != code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="รหัส OTP ไม่ถูกต้อง")
    otp.used = True
    db.add(otp)
    await db.commit()
    return otp


async def _check_trusted_device(db: AsyncSession, user_id: int, device_token: str | None) -> bool:
    if not device_token:
        return False
    result = await db.execute(
        select(TrustedDevice).where(
            TrustedDevice.device_token == device_token,
            TrustedDevice.user_id == user_id,
            TrustedDevice.expires_at > datetime.now(timezone.utc),
        )
    )
    device = result.scalar_one_or_none()
    if not device:
        return False
    device.last_used_at = datetime.now(timezone.utc)
    db.add(device)
    await db.commit()
    return True


async def _create_trusted_device(db: AsyncSession, user_id: int) -> TrustedDevice:
    now = datetime.now(timezone.utc)
    device = TrustedDevice(
        user_id=user_id,
        expires_at=now + timedelta(days=DEVICE_TRUST_DAYS),
        created_at=now,
        last_used_at=now,
    )
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(
        (User.username == body.username) | (User.email == body.username)
    ))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    if user.email:
        # Skip OTP if device is trusted
        if await _check_trusted_device(db, user.user_id, body.device_token):
            token = create_access_token(user.user_id)
            return LoginResponse(access_token=token)
        otp = await _create_otp(db, user.user_id, "login")
        await send_otp_email(user.email, f"{user.first_name} {user.last_name}", otp.code, "login", ref_code=otp.session_token[:6].upper())
        return LoginResponse(requires_2fa=True, otp_session=otp.session_token)

    token = create_access_token(user.user_id)
    return LoginResponse(access_token=token)


@router.post("/verify-otp", response_model=LoginResponse)
async def verify_otp(body: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    otp = await _verify_otp(db, body.otp_session, body.code)
    if otp.purpose != "login":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP ไม่ถูกประเภท")
    token = create_access_token(otp.user_id)
    device_token = None
    if body.remember_device:
        device = await _create_trusted_device(db, otp.user_id)
        device_token = device.device_token
    return LoginResponse(access_token=token, device_token=device_token)


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


class UserMeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: str | None = None


@router.patch("/me", response_model=UserOut)
async def update_me(
    body: UserMeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    is_admin = current_user.is_superuser or 'manage_users' in (current_user.roles or [])
    if (body.first_name is not None or body.last_name is not None) and not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="เฉพาะผู้ที่มีสิทธิ์จัดการบัญชีเท่านั้นที่สามารถเปลี่ยนชื่อ-นามสกุลได้")
    if body.first_name is not None:
        current_user.first_name = body.first_name
    if body.last_name is not None:
        current_user.last_name = body.last_name
    if body.username is not None and body.username != current_user.username:
        existing = await db.execute(select(User).where(User.username == body.username))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ชื่อผู้ใช้นี้มีอยู่แล้ว")
        current_user.username = body.username
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/change-password/request", status_code=status.HTTP_200_OK)
async def request_change_password(
    body: RequestChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="รหัสผ่านปัจจุบันไม่ถูกต้อง")
    if len(body.new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร")

    new_hash = hash_password(body.new_password)

    if current_user.email:
        otp = await _create_otp(db, current_user.user_id, "change_password", payload=new_hash)
        await send_otp_email(current_user.email, f"{current_user.first_name} {current_user.last_name}", otp.code, "change_password", ref_code=otp.session_token[:6].upper())
        return {"requires_otp": True, "otp_session": otp.session_token}

    # No email — apply directly
    current_user.password_hash = new_hash
    db.add(current_user)
    await db.commit()
    return {"requires_otp": False}


@router.post("/change-password/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_change_password(
    body: ConfirmChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    otp = await _verify_otp(db, body.otp_session, body.code)
    if otp.purpose != "change_password" or otp.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP ไม่ถูกต้อง")
    if not otp.payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ข้อมูลรหัสผ่านหาย กรุณาลองใหม่")
    current_user.password_hash = otp.payload
    db.add(current_user)
    await db.commit()


@router.post("/change-email/request", status_code=status.HTTP_200_OK)
async def request_change_email(
    body: RequestChangeEmailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not body.new_email or "@" not in body.new_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="อีเมลไม่ถูกต้อง")
    if body.new_email == current_user.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="อีเมลนี้เหมือนกับอีเมลปัจจุบัน")
    existing = await db.execute(select(User).where(User.email == body.new_email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="อีเมลนี้ถูกใช้งานโดยบัญชีอื่นแล้ว")
    otp = await _create_otp(db, current_user.user_id, "change_email", payload=body.new_email)
    full_name = f"{current_user.first_name} {current_user.last_name}"
    await send_otp_email(body.new_email, full_name, otp.code, "change_email", ref_code=otp.session_token[:6].upper())
    return {"otp_session": otp.session_token}


@router.post("/change-email/confirm", response_model=UserOut)
async def confirm_change_email(
    body: ConfirmChangeEmailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    otp = await _verify_otp(db, body.otp_session, body.code)
    if otp.purpose != "change_email" or otp.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP ไม่ถูกต้อง")
    if not otp.payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ข้อมูลอีเมลหาย กรุณาลองใหม่")
    current_user.email = otp.payload
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


# Legacy endpoint kept for backward compatibility (no 2FA — for accounts without email)
@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="รหัสผ่านปัจจุบันไม่ถูกต้อง")
    if len(body.new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร")
    current_user.password_hash = hash_password(body.new_password)
    db.add(current_user)
    await db.commit()


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email, User.is_active == True))  # noqa: E712
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบบัญชีที่ผูกกับอีเมลนี้")

    reset_token = PasswordResetToken(
        user_id=user.user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        created_at=datetime.now(timezone.utc),
    )
    db.add(reset_token)
    await db.commit()
    await db.refresh(reset_token)

    await send_reset_password_email(user.email, f"{user.first_name} {user.last_name}", reset_token.token)
    return {"message": "หากอีเมลนี้มีในระบบ คุณจะได้รับลิงก์รีเซ็ตรหัสผ่าน"}


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    row = await db.get(PasswordResetToken, body.token)
    if not row or row.used or row.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ลิงก์ไม่ถูกต้องหรือหมดอายุแล้ว")
    if len(body.new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร")

    user = await db.get(User, row.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ไม่พบบัญชีผู้ใช้")

    user.password_hash = hash_password(body.new_password)
    row.used = True
    db.add(user)
    db.add(row)
    await db.commit()


# ─── Admin-only user management ──────────────────────────────────────────────

@router.get("/staff")
async def list_staff(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    """Return users eligible for nurse assignment — must have view_cases role."""
    result = await db.execute(select(User).where(User.is_active == True).order_by(User.first_name, User.last_name))  # noqa: E712
    users = [u for u in result.scalars().all() if 'view_cases' in (u.roles or [])]
    return [{"user_id": u.user_id, "full_name": f"{u.first_name} {u.last_name}"} for u in users]


@router.get("/users", response_model=list[UserOut], dependencies=[Depends(require_admin)])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.username == body.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ชื่อผู้ใช้นี้มีอยู่แล้ว")
    if len(body.password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร")

    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        roles=body.roles or ["nurse"],
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    if body.email:
        await send_welcome_email(body.email, f"{body.first_name} {body.last_name}", body.username, body.password)

    return user


@router.patch("/users/{user_id}", response_model=UserOut)
async def update_user(user_id: int, body: UserUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_admin)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบผู้ใช้")
    if body.username is not None and body.username != user.username:
        existing = await db.execute(select(User).where(User.username == body.username))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ชื่อผู้ใช้นี้มีอยู่แล้ว")
        user.username = body.username
    if body.first_name is not None:
        user.first_name = body.first_name
    if body.last_name is not None:
        user.last_name = body.last_name
    if body.email is not None:
        if body.email and body.email != user.email:
            dup = await db.execute(select(User).where(User.email == body.email))
            if dup.scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="อีเมลนี้ถูกใช้งานโดยบัญชีอื่นแล้ว")
        user.email = body.email
    if body.password is not None:
        if len(body.password) < 6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร")
        user.password_hash = hash_password(body.password)
    if body.roles is not None:
        old_roles = list(user.roles or [])
        old_has = 'manage_users' in old_roles
        new_has = 'manage_users' in body.roles
        if old_has != new_has and not current_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="เฉพาะ superuser เท่านั้นที่สามารถเพิ่ม/ถอดสิทธิ์จัดการบัญชีได้")
        if user.is_superuser and not new_has:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ไม่สามารถถอดสิทธิ์จัดการบัญชีจาก superuser ได้")
        user.roles = body.roles
        # Notify user by email if roles changed
        if user.email and set(old_roles) != set(body.roles):
            changer = f"{current_user.first_name} {current_user.last_name}"
            await send_permission_change_email(user.email, f"{user.first_name} {user.last_name}", old_roles, body.roles, changer)
    if body.is_active is not None:
        user.is_active = body.is_active
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_admin)):
    if user_id == current_user.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ไม่สามารถลบบัญชีของตัวเองได้")
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบผู้ใช้")
    if user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ไม่สามารถลบบัญชี superuser ได้")
    await db.delete(user)
    await db.commit()
