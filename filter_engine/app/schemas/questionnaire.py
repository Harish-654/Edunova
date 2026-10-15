import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class QuestionOption(BaseModel):
    value: str
    label: str
    fields: list[str] = []


class QuestionOut(BaseModel):
    id: str
    prompt: str
    type: str
    options: list[QuestionOption] = []


class QuestionnaireSubmit(BaseModel):
    answers: dict[str, str | int | float | list[str]]


class QuestionnaireResult(BaseModel):
    derived_statement: str
    derived_fields: list[str]
    career_interest_statement: str
    profile_updated: bool


class QuestionnaireStored(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    response_id: uuid.UUID
    answers: dict
    derived_statement: str | None = None
    derived_fields: list[str] | None = None
    created_at: datetime
