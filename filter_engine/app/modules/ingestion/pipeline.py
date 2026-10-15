from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import IngestionAnomalyLog, RawStagingPayload, ScrapingSource
from app.modules.ingestion.parser import parse_page
from app.modules.ingestion.scraper import fetch_page
from app.schemas.admin import CrawlResultOut

MAX_STORED_CHARS = 200_000


async def run_source(session: AsyncSession, source: ScrapingSource) -> CrawlResultOut:
    try:
        html = await fetch_page(source.target_url)
    except Exception as exc:
        payload = RawStagingPayload(
            source_id=source.source_id,
            raw_html_or_json=f"FETCH_ERROR: {exc}",
            is_processed=True,
        )
        session.add(payload)
        await session.commit()
        await session.refresh(payload)
        session.add(
            IngestionAnomalyLog(
                payload_id=payload.payload_id,
                error_code="FETCH_FAILED",
                missing_fields=["raw_html"],
            )
        )
        await session.commit()
        return CrawlResultOut(
            source_id=source.source_id,
            target_name=source.target_name,
            fetched=False,
            missing_fields=["raw_html"],
            error=str(exc),
        )

    fields, missing = parse_page(html)
    payload = RawStagingPayload(
        source_id=source.source_id,
        raw_html_or_json=html[:MAX_STORED_CHARS],
        is_processed=not missing,
    )
    session.add(payload)
    await session.commit()
    await session.refresh(payload)

    if missing:
        session.add(
            IngestionAnomalyLog(
                payload_id=payload.payload_id,
                error_code="MISSING_FIELDS",
                missing_fields=missing,
            )
        )
        await session.commit()

    return CrawlResultOut(
        source_id=source.source_id,
        target_name=source.target_name,
        fetched=True,
        missing_fields=missing,
        error=None,
    )


async def run_all_active(session: AsyncSession) -> list[CrawlResultOut]:
    return await run_sources(session)


async def run_sources(session: AsyncSession, source_id=None) -> list[CrawlResultOut]:
    statement = select(ScrapingSource)
    if source_id is not None:
        statement = statement.where(ScrapingSource.source_id == source_id)
    else:
        statement = statement.where(ScrapingSource.is_active.is_(True))
    sources = (await session.scalars(statement)).all()
    results: list[CrawlResultOut] = []
    for source in sources:
        results.append(await run_source(session, source))
    return results
