import uuid

from sqlalchemy import ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Scholarship(Base):
    __tablename__ = "scholarships"

    scholarship_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255))
    provider_name: Mapped[str | None] = mapped_column(String(255), default=None)
    max_amount: Mapped[float | None] = mapped_column(Numeric(12, 2), default=None)
    max_income_limit: Mapped[float | None] = mapped_column(Numeric(12, 2), default=None)


class ScholarshipExamMapping(Base):
    __tablename__ = "scholarship_exam_mappings"

    mapping_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    scholarship_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("scholarships.scholarship_id", ondelete="CASCADE")
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exams.exam_id", ondelete="CASCADE")
    )
