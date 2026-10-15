import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class ScheduleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    schedule_id: uuid.UUID
    application_start_date: date | None = None
    application_end_date: date | None = None
    exam_date: date | None = None
    academic_year: int


class EligibilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    max_age: int | None = None
    min_qualifying_percentage: float | None = None
    required_degree: str | None = None
    max_family_income: float | None = None


class ExamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    exam_id: uuid.UUID
    exam_code: str
    exam_name: str
    description: str | None = None
    official_url: str | None = None
    conducting_body: str | None = None
    exam_level: str | None = None
    application_fee: str | None = None


class ExamDetailOut(ExamOut):
    schedules: list[ScheduleOut] = []
    eligibility: EligibilityOut | None = None
