from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.entities import Exam, ExamSchedule
from app.schemas.schemas import (
    ExamDetailOut,
    ExamListOut,
    ExamOut,
    ScheduleOut,
)

router = APIRouter(prefix="/exams", tags=["catalog"])


@router.get("", response_model=ExamListOut)
async def list_exams(
    limit: int = Query(default=50, le=500),
    offset: int = 0,
    q: str | None = None,
    level: str | None = None,
    conducting_body: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Exam)
    if q:
        stmt = stmt.where(Exam.exam_name.ilike(f"%{q}%"))
    if level:
        stmt = stmt.where(Exam.exam_level == level.upper())
    if conducting_body:
        stmt = stmt.where(Exam.conducting_body.ilike(f"%{conducting_body}%"))
    stmt = stmt.order_by(Exam.exam_name).limit(limit).offset(offset)

    exams = (await db.execute(stmt)).scalars().all()
    return ExamListOut(
        count=len(exams),
        data=[ExamOut.model_validate(e) for e in exams],
    )


@router.get("/{exam_id}", response_model=ExamDetailOut)
async def get_exam(exam_id: UUID, db: AsyncSession = Depends(get_db)):
    exam = (
        await db.execute(
            select(Exam)
            .options(selectinload(Exam.schedules), selectinload(Exam.eligibility))
            .where(Exam.exam_id == exam_id)
        )
    ).scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return ExamDetailOut.model_validate(exam)


@router.get("/{exam_id}/schedules", response_model=list[ScheduleOut])
async def get_exam_schedules(exam_id: UUID, db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(ExamSchedule).where(ExamSchedule.exam_id == exam_id)
        )
    ).scalars().all()
    return [ScheduleOut.model_validate(r) for r in rows]