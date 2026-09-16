"""Semantic vector matcher + composite scorer.

Stage 2 of the hybrid filter: for exams that pass the hard gate, cosine
similarity between the student's career-interest embedding and the exam
embedding is computed with pgvector, then blended with preference-array
overlays into the final weighted `composite_score`.
"""

import re

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.ingestion.embedder import embedding_service


def preference_overlap(
    preferred_fields: list[str], exam_corpus: str
) -> float:
    """0..1 fraction of the student's preferred fields mentioned in an exam."""
    if not preferred_fields:
        return 1.0
    corpus_lower = (exam_corpus or "").lower()
    hits = 0
    for field_token in preferred_fields:
        token = re.sub(r"[^a-z0-9 ]", " ", str(field_token).lower()).strip()
        if not token:
            continue
        if any(word in corpus_lower for word in token.split()):
            hits += 1
    return round(hits / len(preferred_fields), 4) if preferred_fields else 1.0


def composite_score(
    semantic: float | None, field_overlay: float | None
) -> float | None:
    """Final weighted percentage match."""
    if semantic is None and field_overlay is None:
        return None
    semantic = semantic if semantic is not None else 0.0
    field_overlay = field_overlay if field_overlay is not None else 0.0
    raw = (
        settings.SEMANTIC_WEIGHT * semantic
        + settings.PREFERENCE_WEIGHT * field_overlay
    )
    return round(raw * 100, 2)


async def semantic_similarity(
    db: AsyncSession, interest_embedding: str, exam_id
) -> float | None:
    """pgvector cosine similarity: `1 - (embedding <=> interest)`."""
    row = (
        await db.execute(
            text(
                """
                SELECT 1 - (embedding_vector <=> CAST(:interest AS vector)) AS similarity
                FROM exams
                WHERE exam_id = :exam_id AND embedding_vector IS NOT NULL;
                """
            ),
            {"interest": interest_embedding, "exam_id": exam_id},
        )
    ).fetchone()
    return round(float(row.similarity), 4) if row and row.similarity is not None else None


def embed_interest(statement: str) -> str:
    return embedding_service.to_vector_literal(statement or "")