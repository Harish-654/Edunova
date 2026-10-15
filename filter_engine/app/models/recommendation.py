import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Numeric, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RecommendationCache(Base):
    __tablename__ = "recommendation_cache"
    __table_args__ = (UniqueConstraint("student_id", "exam_id"),)

    cache_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.student_id", ondelete="CASCADE")
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exams.exam_id", ondelete="CASCADE")
    )
    deterministic_eligible: Mapped[bool] = mapped_column(Boolean)
    semantic_match_score: Mapped[float | None] = mapped_column(Numeric(5, 4), default=None)
    composite_score: Mapped[float | None] = mapped_column(Numeric(5, 2), default=None)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())
