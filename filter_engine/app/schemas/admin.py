import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_id: uuid.UUID
    target_name: str
    target_url: str
    cron_expression: str | None = None
    is_active: bool


class SourceCreate(BaseModel):
    target_name: str
    target_url: str
    cron_expression: str = "0 0 * * *"
    is_active: bool = True


class PayloadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payload_id: uuid.UUID
    source_id: uuid.UUID
    fetched_at: datetime
    is_processed: bool


class AnomalyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    log_id: uuid.UUID
    payload_id: uuid.UUID
    error_code: str
    missing_fields: list[str] | None = None
    logged_at: datetime


class CrawlResultOut(BaseModel):
    source_id: uuid.UUID
    target_name: str
    fetched: bool
    missing_fields: list[str] = []
    error: str | None = None


class OverviewOut(BaseModel):
    students: int
    exams: int
    scholarships: int
    sources: int
    payloads: int
    anomalies: int
