import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import require_admin
from app.models import IngestionAnomalyLog, RawStagingPayload, ScrapingSource
from app.modules.ingestion.pipeline import run_sources
from app.schemas.admin import (
    AnomalyOut,
    CrawlResultOut,
    PayloadOut,
    SourceCreate,
    SourceOut,
)

router = APIRouter(
    prefix="/ingestion", tags=["ingestion"], dependencies=[Depends(require_admin)]
)


@router.get("/sources", response_model=list[SourceOut])
async def list_sources(session: AsyncSession = Depends(get_session)):
    return (
        await session.scalars(select(ScrapingSource).order_by(ScrapingSource.target_name))
    ).all()


@router.post("/sources", response_model=SourceOut, status_code=201)
async def create_source(
    payload: SourceCreate, session: AsyncSession = Depends(get_session)
):
    source = ScrapingSource(**payload.model_dump())
    session.add(source)
    await session.commit()
    await session.refresh(source)
    return source


@router.post("/run", response_model=list[CrawlResultOut])
async def run_crawl(
    source_id: uuid.UUID | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    return await run_sources(session, source_id)


@router.get("/payloads", response_model=list[PayloadOut])
async def list_payloads(
    limit: int = Query(default=20, le=100),
    session: AsyncSession = Depends(get_session),
):
    statement = (
        select(RawStagingPayload)
        .order_by(RawStagingPayload.fetched_at.desc())
        .limit(limit)
    )
    return (await session.scalars(statement)).all()


@router.get("/anomalies", response_model=list[AnomalyOut])
async def list_anomalies(
    limit: int = Query(default=20, le=100),
    session: AsyncSession = Depends(get_session),
):
    statement = (
        select(IngestionAnomalyLog)
        .order_by(IngestionAnomalyLog.logged_at.desc())
        .limit(limit)
    )
    return (await session.scalars(statement)).all()
