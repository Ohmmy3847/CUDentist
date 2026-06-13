from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    consent_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_hn: Mapped[str] = mapped_column(String(32), ForeignKey("patients.hn", ondelete="CASCADE"), nullable=False, index=True)
    consented_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    # "public_form" | "verbal" | "paper"
    method: Mapped[str] = mapped_column(String(32), nullable=False, default="public_form")
    form_token: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
