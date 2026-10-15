import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import (
    EligibilityRule,
    Exam,
    ExamSchedule,
    Scholarship,
    ScholarshipExamMapping,
)
from app.schemas.exam import EligibilityOut, ExamDetailOut, ExamOut, ScheduleOut
from app.schemas.scholarship import ScholarshipOut

router = APIRouter(tags=["catalog"])


@router.get("/exams", response_model=list[ExamOut])
async def list_exams(
    level: str | None = Query(default=None),
    search: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    statement = select(Exam)
    if level:
        statement = statement.where(Exam.exam_level == level.upper())
    if search:
        statement = statement.where(Exam.exam_name.ilike(f"%{search}%"))
    statement = statement.order_by(Exam.exam_name)
    return (await session.scalars(statement)).all()


@router.get("/exams/{exam_id}", response_model=ExamDetailOut)
async def get_exam(exam_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    exam = await session.get(Exam, exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")
    schedules = (
        await session.scalars(
            select(ExamSchedule)
            .where(ExamSchedule.exam_id == exam_id)
            .order_by(ExamSchedule.academic_year.desc())
        )
    ).all()
    eligibility = await session.scalar(
        select(EligibilityRule).where(EligibilityRule.exam_id == exam_id)
    )
    detail = ExamDetailOut.model_validate(exam)
    detail.schedules = [ScheduleOut.model_validate(item) for item in schedules]
    detail.eligibility = (
        EligibilityOut.model_validate(eligibility) if eligibility else None
    )
    return detail


@router.get("/scholarships", response_model=list[ScholarshipOut])
async def list_scholarships(session: AsyncSession = Depends(get_session)):
    return (await session.scalars(select(Scholarship).order_by(Scholarship.title))).all()


@router.get("/scholarships/exam/{exam_id}", response_model=list[ScholarshipOut])
async def scholarships_for_exam(
    exam_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    statement = (
        select(Scholarship)
        .join(
            ScholarshipExamMapping,
            ScholarshipExamMapping.scholarship_id == Scholarship.scholarship_id,
        )
        .where(ScholarshipExamMapping.exam_id == exam_id)
        .order_by(Scholarship.title)
    )
    return (await session.scalars(statement)).all()


@router.get("/scholarships/{scholarship_id}", response_model=ScholarshipOut)
async def get_scholarship(
    scholarship_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    scholarship = await session.get(Scholarship, scholarship_id)
    if scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    return scholarship
