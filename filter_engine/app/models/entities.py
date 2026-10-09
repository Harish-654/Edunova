import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator, VARCHAR

from app.core.database import Base


class VectorType(TypeDecorator):
    impl = VARCHAR
    cache_ok = True

    def __init__(self, dimensions: int = 1536):
        super().__init__()
        self.dimensions = dimensions

    def get_col_spec(self, **kw) -> str:
        return f"vector({self.dimensions})"


class Student(Base):
    __tablename__ = "students"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str | None] = mapped_column(String(50))
    state_of_residence: Mapped[str | None] = mapped_column(String(100))
    annual_family_income: Mapped[float | None] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    marks: Mapped[list["StudentMark"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    preferences: Mapped[list["StudentPreference"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )


class StudentPreference(Base):
    __tablename__ = "student_preferences"

    preference_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.student_id", ondelete="CASCADE")
    )
    preferred_fields: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    preferred_locations: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    career_interest_statement: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    student: Mapped[Student] = relationship(back_populates="preferences")


class StudentMark(Base):
    __tablename__ = "student_marks"

    mark_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.student_id", ondelete="CASCADE")
    )
    qualifying_degree: Mapped[str] = mapped_column(String(100), nullable=False)
    overall_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    graduation_year: Mapped[int] = mapped_column(Integer, nullable=False)

    student: Mapped[Student] = relationship(back_populates="marks")


class Exam(Base):
    __tablename__ = "exams"

    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exam_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    exam_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    official_url: Mapped[str | None] = mapped_column(String(500))
    embedding_vector: Mapped[str | None] = mapped_column(VectorType())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    schedules: Mapped[list["ExamSchedule"]] = relationship(
        back_populates="exam", cascade="all, delete-orphan"
    )
    eligibility: Mapped[list["EligibilityRule"]] = relationship(
        back_populates="exam", cascade="all, delete-orphan"
    )


class ExamSchedule(Base):
    __tablename__ = "exam_schedules"

    schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exams.exam_id", ondelete="CASCADE")
    )
    application_start_date: Mapped[date | None] = mapped_column(Date)
    application_end_date: Mapped[date | None] = mapped_column(Date)
    exam_date: Mapped[date | None] = mapped_column(Date)
    academic_year: Mapped[int] = mapped_column(Integer, nullable=False)

    exam: Mapped[Exam] = relationship(back_populates="schedules")


class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"

    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exams.exam_id", ondelete="CASCADE")
    )
    max_age: Mapped[int | None] = mapped_column(Integer)
    min_qualifying_percentage: Mapped[float | None] = mapped_column(Numeric(5, 2))
    required_degree: Mapped[str | None] = mapped_column(String(100))
    max_family_income: Mapped[float | None] = mapped_column(Numeric(12, 2))

    exam: Mapped[Exam] = relationship(back_populates="eligibility")


class RecommendationCache(Base):
    __tablename__ = "recommendation_cache"
    __table_args__ = (UniqueConstraint("student_id", "exam_id"),)

    cache_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.student_id", ondelete="CASCADE")
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exams.exam_id", ondelete="CASCADE")
    )
    deterministic_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False)
    semantic_match_score: Mapped[float | None] = mapped_column(Numeric(5, 4))
    composite_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Scholarship(Base):
    __tablename__ = "scholarships"

    scholarship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_name: Mapped[str | None] = mapped_column(String(255))
    max_amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    max_income_limit: Mapped[float | None] = mapped_column(Numeric(12, 2))


class ScholarshipExamMapping(Base):
    __tablename__ = "scholarship_exam_mappings"

    mapping_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scholarship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scholarships.scholarship_id", ondelete="CASCADE")
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exams.exam_id", ondelete="CASCADE")
    )