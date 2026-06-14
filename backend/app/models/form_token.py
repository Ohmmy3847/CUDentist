import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FormToken(Base):
    __tablename__ = "form_tokens"

    token: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_hn: Mapped[str] = mapped_column(String(32), ForeignKey("patients.hn"), nullable=False, index=True)
    schedule_date: Mapped[str | None] = mapped_column(String(32))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(64))
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    line_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    form_url: Mapped[str | None] = mapped_column(String(512))  # stored at creation time
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
