from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Patient(Base):
    __tablename__ = "patients"

    hn: Mapped[str] = mapped_column(String(32), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    gender: Mapped[str | None] = mapped_column(String(16))
    date_of_birth: Mapped[str | None] = mapped_column(String(16))
    phone: Mapped[str | None] = mapped_column(String(32))
    procedures: Mapped[list | None] = mapped_column(JSONB)
    follow_up_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    follow_up_schedules: Mapped[list | None] = mapped_column(JSONB)
    responsible_person: Mapped[str | None] = mapped_column(String(128))
    responsible_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    extra_info: Mapped[dict | None] = mapped_column(JSONB)
    line_user_id: Mapped[str | None] = mapped_column(String(64), index=True)
    line_reg_code: Mapped[str | None] = mapped_column(String(8), unique=True)
    line_display_name: Mapped[str | None] = mapped_column(String(256))
    line_picture_url: Mapped[str | None] = mapped_column(String(1000))

    assessments: Mapped[list["Assessment"]] = relationship("Assessment", back_populates="patient", lazy="select", cascade="all, delete-orphan")  # noqa: F821
    responsible_nurse: Mapped["User | None"] = relationship("User", foreign_keys=[responsible_user_id], lazy="select")  # noqa: F821
