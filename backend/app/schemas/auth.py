from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str
    device_token: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    access_token: str | None = None
    token_type: str = "bearer"
    requires_2fa: bool = False
    otp_session: str | None = None
    device_token: str | None = None  # returned after OTP success when remember_device=True


class VerifyOTPRequest(BaseModel):
    otp_session: str
    code: str
    remember_device: bool = False


class RequestChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ConfirmChangePasswordRequest(BaseModel):
    otp_session: str
    code: str


class RequestChangeEmailRequest(BaseModel):
    new_email: str


class ConfirmChangeEmailRequest(BaseModel):
    otp_session: str
    code: str


class UserOut(BaseModel):
    user_id: int
    username: str
    first_name: str
    last_name: str
    email: str | None
    roles: list[str]
    is_active: bool
    is_superuser: bool

    model_config = {"from_attributes": True}


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class UserCreate(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    email: str | None = None
    roles: list[str] = ["nurse"]


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: str | None = None
    password: str | None = None
    roles: list[str] | None = None
    is_active: bool | None = None
