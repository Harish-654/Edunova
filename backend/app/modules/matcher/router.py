from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.entities import (
    EligibilityRule,
    Exam,
    ExamSchedule,
    Scholarship,
    ScholarshipExamMapping,
    Student,
    StudentMark,
    StudentPreference,
)
from app.modules.matcher.cache import clear_student_cache, upsert_match
from app.modules.matcher.eligibility import (
    EligibilityBreakdown,
    evaluate_eligibility,
)
from app.modules.matcher.scorer import (
    composite_score,
    embed_interest,
    preference_overlap,
    semantic_similarity,
)
from app.schemas.schemas import (
    ExamOut,
    MatchResponse,
    ScheduleOut,
    ScholarshipOut,
)

router = APIRouter(prefix="/match", tags=["match"])


def _exam_out(exam: Exam) -> ExamOut:
    return ExamOut.model_validate(exam)


def _schedule_out(exam: Exam) -> ScheduleOut | None:
    schedule = next(iter(exam.schedules), None)
    return ScheduleOut.model_validate(schedule) if schedule else None


def _eligibility_dict(b: EligibilityBreakdown) -> dict:
    return {
        "age": b.age,
        "percentage": b.percentage,
        "degree": b.degree,
        "income": b.income,
        "detail": b.detail,
    }


async def _compute_for_student(
    db: AsyncSession, student: Student, marks: StudentMark | None,
    preferences: StudentPreference | None,
) -> list[dict]:
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

    # Scholarships keyed by exam for the financial-aid drawer.
    scholarship_map: dict[UUID, list[Scholarship]] = {}
    if exams:
        rows = (
            await db.execute(
                select(Scholarship, ScholarshipExamMapping.exam_id)
                .join(
                    ScholarshipExamMapping,
                    Scholarship.scholarship_id == ScholarshipExamMapping.scholarship_id,
                )
                .where(
                    ScholarshipExamMapping.exam_id.in_([e.exam_id for e in exams])
                )
            )
        ).fetchall()
        for scholarship, exam_id in rows:
            scholarship_map.setdefault(exam_id, []).append(scholarship)

    results: list[dict] = []
    for exam in exams:
        rule = next(iter(exam.eligibility), None)
        if rule is None:
            rule = EligibilityRule(exam_id=exam.exam_id)
        breakdown = evaluate_eligibility(student, marks, rule)

        semantic: float | None = None
        final_composite: float | None = None
        if breakdown.eligible:
            semantic = await semantic_similarity(db, interest_embedding, exam.exam_id)
            overlay = preference_overlap(
                preferred_fields,
                " ".join(
                    filter(
                        None,
                        [exam.exam_name, exam.description,
                         exam.conducting_body, exam.exam_level],
                    )
                ),
            )
            final_composite = composite_score(semantic, overlay)
        else:
            final_composite = 0.0

        await upsert_match(
            db, student, exam, breakdown.eligible, semantic, final_composite
        )

        scholarships = scholarship_map.get(exam.exam_id, [])
        results.append(
            {
                "exam": _exam_out(exam),
                "schedule": _schedule_out(exam),
                "deterministic_eligible": breakdown.eligible,
                "semantic_match_score": semantic,
                "composite_score": final_composite,
                "eligibility": _eligibility_dict(breakdown),
                "scholarships": [
                    ScholarshipOut.model_validate(s) for s in scholarships
                ],
            }
        )

    await db.commit()

    results.sort(
        key=lambda r: r["composite_score"] or 0.0, reverse=True
    )
    return results


async def _load_profile(db: AsyncSession, student_id: UUID):
    student = await db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
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


@router.post("/student/{student_id}/compute", response_model=MatchResponse)
async def compute_matches(student_id: UUID, db: AsyncSession = Depends(get_db)):
    student, marks, preferences = await _load_profile(db, student_id)
    await clear_student_cache(db, student_id)
    results = await _compute_for_student(db, student, marks, preferences)
    return MatchResponse(student_id=student_id, results=results)


@router.get("/student/{student_id}/recommendations", response_model=MatchResponse)
async def get_recommendations(student_id: UUID, db: AsyncSession = Depends(get_db)):
    student, marks, preferences = await _load_profile(db, student_id)

    # Fall back to a synchronous compute if the cache is empty/stale.
    if preferences is None or not preferences.career_interest_statement:
        raise HTTPException(
            status_code=400,
            detail="Complete your career-interest preferences before requesting matches.",
        )

    results = await _compute_for_student(db, student, marks, preferences)
    return MatchResponse(student_id=student_id, results=results)