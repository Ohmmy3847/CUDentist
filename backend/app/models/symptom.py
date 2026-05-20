from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Symptom(Base):
    __tablename__ = "symptoms"

    symptom_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symptom_name: Mapped[str] = mapped_column(String(128), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), default="low")  # low | medium | high
    recommendation: Mapped[str | None] = mapped_column(Text)
    management_guidance: Mapped[str | None] = mapped_column(Text)
    aliases: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    managed_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"))

    manager: Mapped["User"] = relationship("User", back_populates="symptoms")  # noqa: F821
