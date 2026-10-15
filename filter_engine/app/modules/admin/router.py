import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import require_admin
from app.models import (
    Exam,
    IngestionAnomalyLog,
    RawStagingPayload,
    Scholarship,
    ScholarshipExamMapping,
    ScrapingSource,
    Student,
)
from app.schemas.admin import OverviewOut
from app.schemas.scholarship import ScholarshipCreate, ScholarshipOut, ScholarshipUpdate

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


async def count(session: AsyncSession, model) -> int:
    return await session.scalar(select(func.count()).select_from(model))


@router.get("/overview", response_model=OverviewOut)
async def overview(session: AsyncSession = Depends(get_session)):
    return OverviewOut(
        students=await count(session, Student),
        exams=await count(session, Exam),
        scholarships=await count(session, Scholarship),
        sources=await count(session, ScrapingSource),
        payloads=await count(session, RawStagingPayload),
        anomalies=await count(session, IngestionAnomalyLog),
    )


@router.post("/scholarships", response_model=ScholarshipOut, status_code=201)
async def create_scholarship(
    payload: ScholarshipCreate, session: AsyncSession = Depends(get_session)
):
    scholarship = Scholarship(**payload.model_dump())
    session.add(scholarship)
    await session.commit()
    await session.refresh(scholarship)
    return scholarship


@router.put("/scholarships/{scholarship_id}", response_model=ScholarshipOut)
async def update_scholarship(
    scholarship_id: uuid.UUID,
    payload: ScholarshipUpdate,
    session: AsyncSession = Depends(get_session),
):
    scholarship = await session.get(Scholarship, scholarship_id)
    if scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(scholarship, field, value)
    await session.commit()
    await session.refresh(scholarship)
    return scholarship


@router.delete("/scholarships/{scholarship_id}", status_code=204)
async def delete_scholarship(
    scholarship_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    scholarship = await session.get(Scholarship, scholarship_id)
    if scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    await session.delete(scholarship)
    await session.commit()


@router.post("/scholarships/{scholarship_id}/exams/{exam_id}", status_code=201)
async def map_exam(
    scholarship_id: uuid.UUID,
    exam_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    if await session.get(Scholarship, scholarship_id) is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    if await session.get(Exam, exam_id) is None:
        raise HTTPException(status_code=404, detail="Exam not found")
    existing = await session.scalar(
        select(ScholarshipExamMapping).where(
            ScholarshipExamMapping.scholarship_id == scholarship_id,
            ScholarshipExamMapping.exam_id == exam_id,
        )
    )
    if existing is None:
        session.add(
            ScholarshipExamMapping(scholarship_id=scholarship_id, exam_id=exam_id)
        )
        await session.commit()
    return {"scholarship_id": scholarship_id, "exam_id": exam_id}


@router.delete("/scholarships/{scholarship_id}/exams/{exam_id}", status_code=204)
async def unmap_exam(
    scholarship_id: uuid.UUID,
    exam_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    mapping = await session.scalar(
        select(ScholarshipExamMapping).where(
            ScholarshipExamMapping.scholarship_id == scholarship_id,
            ScholarshipExamMapping.exam_id == exam_id,
        )
    )
    if mapping is not None:
        await session.delete(mapping)
        await session.commit()
