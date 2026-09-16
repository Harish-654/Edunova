from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.entities import Scholarship, ScholarshipExamMapping
from app.schemas.schemas import ScholarshipOut

router = APIRouter(prefix="/scholarships", tags=["scholarships"])


@router.get("", response_model=list[ScholarshipOut])
async def list_scholarships(
    q: str | None = None, db: AsyncSession = Depends(get_db)
):
    stmt = select(Scholarship).order_by(Scholarship.title)
    if q:
        stmt = stmt.where(Scholarship.title.ilike(f"%{q}%"))
    rows = (await db.execute(stmt)).scalars().all()
    return [ScholarshipOut.model_validate(s) for s in rows]


@router.get("/exam/{exam_id}", response_model=list[ScholarshipOut])
async def scholarships_for_exam(exam_id: UUID, db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(Scholarship)
            .join(
                ScholarshipExamMapping,
                Scholarship.scholarship_id == ScholarshipExamMapping.scholarship_id,
            )
            .where(ScholarshipExamMapping.exam_id == exam_id)
            .order_by(Scholarship.title)
        )
    ).scalars().all()
    return [ScholarshipOut.model_validate(s) for s in rows]