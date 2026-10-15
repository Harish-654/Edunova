from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    EligibilityRule,
    Exam,
    RecommendationCache,
    Student,
    StudentMark,
    StudentPreference,
)
from app.modules.matcher.eligibility import check_eligibility
from app.modules.matcher.embedder import to_vector_literal
from app.schemas.match import RecommendationOut

SEMANTIC_WEIGHT = 0.6
OVERLAY_WEIGHT = 0.4


def matched_fields(exam: Exam, fields: list[str]) -> list[str]:
    corpus = " ".join(
        part
        for part in (exam.exam_name, exam.description, exam.exam_level, exam.conducting_body)
        if part
    ).lower()
    return [field for field in fields if field.lower() in corpus]


async def upsert_cache(
    session: AsyncSession,
    student_id,
    exam_id,
    eligible: bool,
    semantic_score: float,
    composite_score: float,
) -> None:
    statement = pg_insert(RecommendationCache).values(
        student_id=student_id,
        exam_id=exam_id,
        deterministic_eligible=eligible,
        semantic_match_score=round(semantic_score, 4),
        composite_score=composite_score,
    )
    statement = statement.on_conflict_do_update(
        index_elements=[RecommendationCache.student_id, RecommendationCache.exam_id],
        set_={
            "deterministic_eligible": eligible,
            "semantic_match_score": round(semantic_score, 4),
            "composite_score": composite_score,
            "updated_at": func.now(),
        },
    )
    await session.execute(statement)


async def compute_recommendations(
    session: AsyncSession, student: Student
) -> list[RecommendationOut]:
    preference = await session.scalar(
        select(StudentPreference)
        .where(StudentPreference.student_id == student.student_id)
        .order_by(StudentPreference.created_at.desc())
    )
    mark = await session.scalar(
        select(StudentMark).where(StudentMark.student_id == student.student_id)
    )

    statement_text = (
        preference.career_interest_statement if preference else None
    ) or ""
    fields = (preference.preferred_fields if preference else None) or []
    student_text = " ".join(
        part for part in (statement_text, " ".join(fields)) if part
    ).strip()
    if not student_text:
        return []

    literal = to_vector_literal(student_text)
    semantic_rows = await session.execute(
        text(
            "SELECT exam_id, 1 - (embedding_vector <=> "
            f"'{literal}'::vector) AS semantic "
            "FROM exams WHERE embedding_vector IS NOT NULL"
        )
    )
    semantic_scores = {row.exam_id: float(row.semantic) for row in semantic_rows}

    exams = (await session.scalars(select(Exam).order_by(Exam.exam_name))).all()
    rules = {
        rule.exam_id: rule
        for rule in (await session.scalars(select(EligibilityRule))).all()
    }

    age = student.age
    percentage = float(mark.overall_percentage) if mark else None
    degree = mark.qualifying_degree if mark else None
    income = (
        float(student.annual_family_income)
        if student.annual_family_income is not None
        else None
    )

    results: list[RecommendationOut] = []
    for exam in exams:
        reasons = check_eligibility(
            rules.get(exam.exam_id),
            age=age,
            percentage=percentage,
            degree=degree,
            family_income=income,
        )
        eligible = not reasons
        semantic_score = semantic_scores.get(exam.exam_id, 0.0)
        fields_hit = matched_fields(exam, fields)
        overlay = len(fields_hit) / len(fields) if fields else 0.0
        composite = round(
            (SEMANTIC_WEIGHT * semantic_score + OVERLAY_WEIGHT * overlay) * 100, 2
        )
        results.append(
            RecommendationOut(
                exam_id=exam.exam_id,
                exam_code=exam.exam_code,
                exam_name=exam.exam_name,
                exam_level=exam.exam_level,
                conducting_body=exam.conducting_body,
                eligible=eligible,
                semantic_score=round(semantic_score, 4),
                composite_score=composite,
                matched_fields=fields_hit,
                reasons=reasons,
            )
        )
        await upsert_cache(
            session,
            student.student_id,
            exam.exam_id,
            eligible,
            semantic_score,
            composite,
        )

    await session.commit()
    results.sort(key=lambda item: (item.eligible, item.composite_score), reverse=True)
    return results
