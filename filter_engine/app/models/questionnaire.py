import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Text, Uuid, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class QuestionnaireResponse(Base):
    __tablename__ = "questionnaire_responses"

    response_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.student_id", ondelete="CASCADE")
    )
    answers: Mapped[dict] = mapped_column(JSONB)
    derived_statement: Mapped[str | None] = mapped_column(Text, default=None)
    derived_fields: Mapped[list[str] | None] = mapped_column(ARRAY(Text), default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
