"""Recommendation cache manager.

Persists `(student_id, exam_id)` match metrics to `recommendation_cache`
so the frontend renders instant results without recomputing embeddings
on every page load.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Exam, Student


async def upsert_match(
    db: AsyncSession,
    student: Student,
    exam: Exam,
    deterministic_eligible: bool,
    semantic_match_score: float | None,
    composite_score: float | None,
) -> None:
    await db.execute(
        text(
            """
            INSERT INTO recommendation_cache
                (student_id, exam_id, deterministic_eligible, semantic_match_score, composite_score)
            VALUES
                (:student_id, :exam_id, :eligible, :semantic, :composite)
            ON CONFLICT (student_id, exam_id) DO UPDATE SET
                deterministic_eligible = EXCLUDED.deterministic_eligible,
                semantic_match_score   = EXCLUDED.semantic_match_score,
                composite_score        = EXCLUDED.composite_score,
                updated_at             = CURRENT_TIMESTAMP;
            """
        ),
        {
            "student_id": student.student_id,
            "exam_id": exam.exam_id,
            "eligible": deterministic_eligible,
            "semantic": semantic_match_score,
            "composite": composite_score,
        },
    )


async def clear_student_cache(db: AsyncSession, student_id) -> None:
    await db.execute(
        text("DELETE FROM recommendation_cache WHERE student_id = :student_id;"),
        {"student_id": student_id},
    )