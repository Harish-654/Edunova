import uuid

from pydantic import BaseModel, ConfigDict


class ScholarshipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scholarship_id: uuid.UUID
    title: str
    provider_name: str | None = None
    max_amount: float | None = None
    max_income_limit: float | None = None


class ScholarshipCreate(BaseModel):
    title: str
    provider_name: str | None = None
    max_amount: float | None = None
    max_income_limit: float | None = None


class ScholarshipUpdate(BaseModel):
    title: str | None = None
    provider_name: str | None = None
    max_amount: float | None = None
    max_income_limit: float | None = None
