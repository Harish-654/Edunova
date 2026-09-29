from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.entities import (
    EligibilityRule,
    Exam,
    Scholarship,
    ScholarshipExamMapping,
    Student,
    StudentMark,
    StudentPreference,
)
from app.modules.matcher.cache import clear_student_cache, upsert_match
from app.modules.matcher.eligibility import evaluate_eligibility
from app.modules.matcher.scorer import (
    composite_score,
    embed_interest,
    preference_overlap,
    semantic_similarity,
)
from app.schemas.matching import (
    EligibilityBreakdown as EligibilityBreakdownSchema,
    ExamOut,
    MatchResponse,
    MatchResult,
    ScheduleOut,
    ScholarshipOut,
)


async def _load_profile(
    db: AsyncSession, student_id: UUID
) -> tuple[Student, StudentMark | None, StudentPreference | None]:
    student = await db.get(Student, student_id)
    if student is None:
        raise LookupError("Student not found")

    marks = (
        await db.execute(
            select(StudentMark)
            .where(StudentMark.student_id == student_id)
            .order_by(StudentMark.graduation_year.desc())
        )
    ).scalars().first()
    preferences = (
        await db.execute(
            select(StudentPreference)
            .where(StudentPreference.student_id == student_id)
            .order_by(StudentPreference.created_at.desc())
        )
    ).scalars().first()
    return student, marks, preferences


async def compute_matches(db: AsyncSession, student_id: UUID) -> MatchResponse:
    student, marks, preferences = await _load_profile(db, student_id)
    await clear_student_cache(db, student_id)

    exams = (
        await db.execute(
            select(Exam)
            .options(selectinload(Exam.schedules), selectinload(Exam.eligibility))
            .order_by(Exam.exam_name)
        )
    ).scalars().all()

    interest_embedding = embed_interest(
        preferences.career_interest_statement if preferences else ""
    )
    preferred_fields = (preferences.preferred_fields if preferences else None) or []

    scholarship_map: dict[UUID, list[Scholarship]] = {}
    if exams:
        rows = (
            await db.execute(
                select(Scholarship, ScholarshipExamMapping.exam_id)
                .join(
                    ScholarshipExamMapping,
                    Scholarship.scholarship_id
                    == ScholarshipExamMapping.scholarship_id,
                )
                .where(
                    ScholarshipExamMapping.exam_id.in_([exam.exam_id for exam in exams])
                )
            )
        ).fetchall()
        for scholarship, exam_id in rows:
            scholarship_map.setdefault(exam_id, []).append(scholarship)

    results: list[MatchResult] = []
    for exam in exams:
        rule = next(iter(exam.eligibility), None) or EligibilityRule(
            exam_id=exam.exam_id
        )
        breakdown = evaluate_eligibility(student, marks, rule)

        semantic: float | None = None
        final_composite: float | None = 0.0
        if breakdown.eligible:
            semantic = await semantic_similarity(
                db, interest_embedding, exam.exam_id
            )
            corpus = " ".join(filter(None, [exam.exam_name, exam.description]))
            overlay = preference_overlap(preferred_fields, corpus)
            final_composite = composite_score(semantic, overlay)

        await upsert_match(
            db, student, exam, breakdown.eligible, semantic, final_composite
        )

        schedule = next(iter(exam.schedules), None)
        results.append(
            MatchResult(
                exam=ExamOut.model_validate(exam),
                schedule=ScheduleOut.model_validate(schedule) if schedule else None,
                deterministic_eligible=breakdown.eligible,
                semantic_match_score=semantic,
                composite_score=final_composite,
                eligibility=EligibilityBreakdownSchema(
                    age=breakdown.age,
                    percentage=breakdown.percentage,
                    degree=breakdown.degree,
                    income=breakdown.income,
                    detail=breakdown.detail,
                ),
                scholarships=[
                    ScholarshipOut.model_validate(scholarship)
                    for scholarship in scholarship_map.get(exam.exam_id, [])
                ],
            )
        )

    await db.commit()
    results.sort(key=lambda result: result.composite_score or 0.0, reverse=True)
    return MatchResponse(student_id=student_id, results=results)