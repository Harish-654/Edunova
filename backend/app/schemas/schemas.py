from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr as PydanticEmailStr, Field, HttpUrl


# Re-export as plain name used across app
EmailStr = PydanticEmailStr


# ---------- Auth ----------
class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=6)
    age: int = Field(ge=10, le=60)
    category: str | None = None
    state_of_residence: str | None = None
    annual_family_income: float | None = Field(default=None, ge=0)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class StudentOut(BaseModel):
    student_id: UUID
    full_name: str
    email: str
    age: int
    category: str | None = None
    state_of_residence: str | None = None
    annual_family_income: float | None = None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: StudentOut


# ---------- Student profile ----------
class MarksUpdate(BaseModel):
    qualifying_degree: str = Field(min_length=1, max_length=100)
    overall_percentage: float = Field(ge=0, le=100)
    graduation_year: int = Field(ge=1990, le=2100)


class PreferencesUpdate(BaseModel):
    preferred_fields: list[str] = []
    preferred_locations: list[str] = []
    career_interest_statement: str = ""


class ProfilePatch(BaseModel):
    age: int | None = Field(default=None, ge=10, le=60)
    category: str | None = None
    state_of_residence: str | None = None
    annual_family_income: float | None = Field(default=None, ge=0)


class StudentProfileOut(StudentOut):
    qualifying_degree: str | None = None
    overall_percentage: float | None = None
    graduation_year: int | None = None
    preferred_fields: list[str] = []
    preferred_locations: list[str] = []
    career_interest_statement: str = ""


# ---------- Catalog ----------
class ExamOut(BaseModel):
    exam_id: UUID
    exam_code: str
    exam_name: str
    description: str | None = None
    official_url: str | None = None
    conducting_body: str | None = None
    exam_level: str | None = None
    application_fee: float | None = None
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


class ExamDetailOut(ExamOut):
    schedules: list[ScheduleOut] = []
    eligibility: list["EligibilityOut"] = []


class EligibilityOut(BaseModel):
    rule_id: UUID
    exam_id: UUID
    max_age: int | None = None
    min_qualifying_percentage: float | None = None
    required_degree: str | None = None
    max_family_income: float | None = None

    model_config = {"from_attributes": True}


class ExamListOut(BaseModel):
    count: int
    data: list[ExamOut]


# ---------- Ingestion ----------
class ScrapingSourceIn(BaseModel):
    target_name: str
    target_url: HttpUrl
    cron_expression: str = "0 0 * * *"


class ScrapingSourceOut(BaseModel):
    source_id: UUID
    target_name: str
    target_url: str
    cron_expression: str
    is_active: bool

    model_config = {"from_attributes": True}


class TriggerScrapeRequest(BaseModel):
    source_id: UUID
    target_url: HttpUrl


class TriggerResponse(BaseModel):
    status: str
    message: str
    target_url: str


class AnomalyOut(BaseModel):
    log_id: UUID
    payload_id: UUID
    error_code: str
    missing_fields: list[str] = []
    logged_at: datetime | None = None

    model_config = {"from_attributes": True}


# ---------- Matcher ----------
class EligibilityBreakdown(BaseModel):
    age: bool | None = None
    percentage: bool | None = None
    degree: bool | None = None
    income: bool | None = None
    detail: list[str] = []


class MatchResult(BaseModel):
    exam: ExamOut
    schedule: ScheduleOut | None = None
    deterministic_eligible: bool
    semantic_match_score: float | None = None
    composite_score: float | None = None
    eligibility: EligibilityBreakdown
    scholarships: list["ScholarshipOut"] = []


class MatchResponse(BaseModel):
    student_id: UUID
    computed_at: datetime | None = None
    results: list[MatchResult]


# ---------- Scholarships ----------
class ScholarshipOut(BaseModel):
    scholarship_id: UUID
    title: str
    provider_name: str | None = None
    max_amount: float | None = None
    max_income_limit: float | None = None

    model_config = {"from_attributes": True}


MatchResult.model_rebuild()