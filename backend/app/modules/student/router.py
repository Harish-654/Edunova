from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.entities import (
    Student,
    StudentMark,
    StudentPreference,
)
from app.schemas.schemas import (
    MarksUpdate,
    PreferencesUpdate,
    ProfilePatch,
    StudentProfileOut,
)

router = APIRouter(prefix="/students", tags=["students"])


async def _get_student(db: AsyncSession, student_id: UUID) -> Student:
    student = await db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


async def _profile_out(db: AsyncSession, student: Student) -> StudentProfileOut:
    marks = (
        await db.execute(
            select(StudentMark)
            .where(StudentMark.student_id == student.student_id)
            .order_by(StudentMark.graduation_year.desc())
        )
    ).scalars().first()
    preferences = (
        await db.execute(
            select(StudentPreference)
            .where(StudentPreference.student_id == student.student_id)
            .order_by(StudentPreference.created_at.desc())
        )
    ).scalars().first()

    return StudentProfileOut(
        student_id=student.student_id,
        full_name=student.full_name,
        email=student.email,
        age=student.age,
        category=student.category,
        state_of_residence=student.state_of_residence,
        annual_family_income=float(student.annual_family_income)
        if student.annual_family_income is not None
        else None,
        qualifying_degree=marks.qualifying_degree if marks else None,
        overall_percentage=float(marks.overall_percentage) if marks else None,
        graduation_year=marks.graduation_year if marks else None,
        preferred_fields=preferences.preferred_fields if preferences else [],
        preferred_locations=preferences.preferred_locations if preferences else [],
        career_interest_statement=(
            preferences.career_interest_statement if preferences else ""
        ),
    )


@router.put("/{student_id}/profile", response_model=StudentProfileOut)
async def patch_profile(
    student_id: UUID, payload: ProfilePatch, db: AsyncSession = Depends(get_db)
):
    student = await _get_student(db, student_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    await db.commit()
    await db.refresh(student)
    return await _profile_out(db, student)


@router.put("/{student_id}/marks", response_model=StudentProfileOut)
async def update_marks(
    student_id: UUID, payload: MarksUpdate, db: AsyncSession = Depends(get_db)
):
    await _get_student(db, student_id)
    # Replace existing marks with the latest academic record.
    existing = (
        await db.execute(select(StudentMark).where(StudentMark.student_id == student_id))
    ).scalars().all()
    for mark in existing:
        await db.delete(mark)
    db.add(
        StudentMark(
            student_id=student_id,
            qualifying_degree=payload.qualifying_degree,
            overall_percentage=payload.overall_percentage,
            graduation_year=payload.graduation_year,
        )
    )
    await db.commit()
    student = await _get_student(db, student_id)
    return await _profile_out(db, student)


@router.put("/{student_id}/preferences", response_model=StudentProfileOut)
async def update_preferences(
    student_id: UUID,
    payload: PreferencesUpdate,
    db: AsyncSession = Depends(get_db),
):
    await _get_student(db, student_id)
    existing = (
        await db.execute(
            select(StudentPreference).where(
                StudentPreference.student_id == student_id
            )
        )
    ).scalars().all()
    for pref in existing:
        await db.delete(pref)
    db.add(
        StudentPreference(
            student_id=student_id,
            preferred_fields=payload.preferred_fields,
            preferred_locations=payload.preferred_locations,
            career_interest_statement=payload.career_interest_statement,
        )
    )
    await db.commit()
    student = await _get_student(db, student_id)
    return await _profile_out(db, student)