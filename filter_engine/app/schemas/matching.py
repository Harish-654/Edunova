from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class ExamOut(BaseModel):
    exam_id: UUID
    exam_code: str
    exam_name: str
    description: str | None = None
    official_url: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ScheduleOut(BaseModel):
    schedule_id: UUID
    exam_id: UUID
    application_start_date: date | None = None
    application_end_date: date | None = None
    exam_date: date | None = None
    academic_year: int

    model_config = {"from_attributes": True}


class EligibilityBreakdown(BaseModel):
    age: bool | None = None
    percentage: bool | None = None
    degree: bool | None = None
    income: bool | None = None
    detail: list[str] = []


class ScholarshipOut(BaseModel):
    scholarship_id: UUID
    title: str
    provider_name: str | None = None
    max_amount: float | None = None
    max_income_limit: float | None = None

    model_config = {"from_attributes": True}


class MatchResult(BaseModel):
    exam: ExamOut
    schedule: ScheduleOut | None = None
    deterministic_eligible: bool
    semantic_match_score: float | None = None
    composite_score: float | None = None
    eligibility: EligibilityBreakdown
    scholarships: list[ScholarshipOut] = []


class MatchResponse(BaseModel):
    student_id: UUID
    computed_at: datetime | None = None
    results: list[MatchResult]