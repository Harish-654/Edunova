import uuid
from datetime import date, datetime

from sqlalchemy import ForeignKey, Numeric, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Exam(Base):
    __tablename__ = "exams"

    exam_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    exam_code: Mapped[str] = mapped_column(String(50), unique=True)
    exam_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, default=None)
    official_url: Mapped[str | None] = mapped_column(String(500), default=None)
    conducting_body: Mapped[str | None] = mapped_column(String(255), default=None)
    exam_level: Mapped[str | None] = mapped_column(String(20), default=None)
    application_fee: Mapped[str | None] = mapped_column(String(100), default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class ExamSchedule(Base):
    __tablename__ = "exam_schedules"

    schedule_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exams.exam_id", ondelete="CASCADE")
    )
    application_start_date: Mapped[date | None] = mapped_column(default=None)
    application_end_date: Mapped[date | None] = mapped_column(default=None)
    exam_date: Mapped[date | None] = mapped_column(default=None)
    academic_year: Mapped[int]


class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"

    rule_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    exam_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exams.exam_id", ondelete="CASCADE")
    )
    max_age: Mapped[int | None] = mapped_column(default=None)
    min_qualifying_percentage: Mapped[float | None] = mapped_column(
        Numeric(5, 2), default=None
    )
    required_degree: Mapped[str | None] = mapped_column(String(100), default=None)
    max_family_income: Mapped[float | None] = mapped_column(Numeric(12, 2), default=None)
