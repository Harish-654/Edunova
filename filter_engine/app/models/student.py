import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Numeric, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Student(Base):
    __tablename__ = "students"

    student_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="student")
    age: Mapped[int | None] = mapped_column(default=None)
    category: Mapped[str | None] = mapped_column(String(50), default=None)
    state_of_residence: Mapped[str | None] = mapped_column(String(100), default=None)
    annual_family_income: Mapped[float | None] = mapped_column(Numeric(12, 2), default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class StudentPreference(Base):
    __tablename__ = "student_preferences"

    preference_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.student_id", ondelete="CASCADE")
    )
    preferred_fields: Mapped[list[str] | None] = mapped_column(ARRAY(Text), default=None)
    preferred_locations: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text), default=None
    )
    career_interest_statement: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class StudentMark(Base):
    __tablename__ = "student_marks"

    mark_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.student_id", ondelete="CASCADE")
    )
    qualifying_degree: Mapped[str] = mapped_column(String(100))
    overall_percentage: Mapped[float] = mapped_column(Numeric(5, 2))
    graduation_year: Mapped[int]
