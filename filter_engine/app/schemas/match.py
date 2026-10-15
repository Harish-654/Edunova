import uuid

from pydantic import BaseModel


class RecommendationOut(BaseModel):
    exam_id: uuid.UUID
    exam_code: str
    exam_name: str
    exam_level: str | None = None
    conducting_body: str | None = None
    eligible: bool
    semantic_score: float
    composite_score: float
    matched_fields: list[str] = []
    reasons: list[str] = []
