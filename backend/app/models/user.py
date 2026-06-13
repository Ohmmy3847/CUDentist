from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Enum, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

# superadmin — full access (owner/IT)
# doctor     — clinical access, sees only assigned patients
# staff      — front-desk: add/edit patients, no clinical notes
UserRole = Enum("superadmin", "doctor", "staff", name="user_role")


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    role: Mapped[str] = mapped_column(UserRole, nullable=False, default="staff")
    roles: Mapped[list] = mapped_column(JSON, nullable=False, default=lambda: ["nurse"])
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    assessments: Mapped[list["Assessment"]] = relationship("Assessment", back_populates="creator", lazy="select")  # noqa: F821
    symptoms: Mapped[list["Symptom"]] = relationship("Symptom", back_populates="manager", lazy="select")  # noqa: F821
