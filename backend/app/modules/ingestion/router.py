from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.ingestion.embedder import embedding_service
from app.modules.ingestion.scraper import run_scraper
from app.schemas.schemas import (
    AnomalyOut,
    ScrapingSourceIn,
    ScrapingSourceOut,
    TriggerResponse,
    TriggerScrapeRequest,
)

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/sources", response_model=ScrapingSourceOut, status_code=201)
async def add_source(
    payload: ScrapingSourceIn, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text(
            """
            INSERT INTO scraping_sources (target_name, target_url, cron_expression)
            VALUES (:name, :url, :cron)
            RETURNING source_id, target_name, target_url, cron_expression, is_active;
            """
        ),
        {
            "name": payload.target_name,
            "url": str(payload.target_url),
            "cron": payload.cron_expression,
        },
    )
    await db.commit()
    row = result.mappings().first()
    return dict(row)


@router.get("/sources", response_model=list[ScrapingSourceOut])
async def list_sources(db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            text(
                "SELECT source_id, target_name, target_url, cron_expression, is_active "
                "FROM scraping_sources ORDER BY target_name;"
            )
        )
    ).fetchall()
    return [dict(r._mapping) for r in rows]


@router.post("/trigger", response_model=TriggerResponse)
async def trigger_ingestion(
    body: TriggerScrapeRequest,
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(run_scraper, body.source_id, str(body.target_url))
    return TriggerResponse(
        status="QUEUED",
        message=f"Scrape job queued for source {body.source_id}",
        target_url=str(body.target_url),
    )


@router.post("/embed-all")
async def embed_all(db: AsyncSession = Depends(get_db)):
    """(Re)generate embeddings for every exam description."""
    exams = (
        await db.execute(
            text(
                "SELECT exam_id, exam_name, description, conducting_body, exam_level "
                "FROM exams;"
            )
        )
    ).fetchall()
    updated = 0
    for exam in exams:
        corpus = " ".join(
            filter(
                None,
                [exam.exam_name, exam.description, exam.conducting_body, exam.exam_level],
            )
        )
        vector_literal = embedding_service.to_vector_literal(corpus)
        await db.execute(
            text(
                "UPDATE exams SET embedding_vector = CAST(:vec AS vector) "
                "WHERE exam_id = :exam_id;"
            ),
            {"vec": vector_literal, "exam_id": exam.exam_id},
        )
        updated += 1
    await db.commit()
    return {"embedded": updated, "provider": "local"}


@router.get("/anomalies", response_model=list[AnomalyOut])
async def list_anomalies(limit: int = 50, db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            text(
                """
                SELECT log_id, payload_id, error_code, missing_fields, logged_at
                FROM ingestion_anomaly_logs
                ORDER BY logged_at DESC LIMIT :limit;
                """
            ),
            {"limit": limit},
        )
    ).fetchall()
    return [
        {
            "log_id": r.log_id,
            "payload_id": r.payload_id,
            "error_code": r.error_code,
            "missing_fields": r.missing_fields or [],
            "logged_at": r.logged_at,
        }
        for r in rows
    ]


@router.get("/health")
async def ingestion_health():
    return {"status": "ok"}