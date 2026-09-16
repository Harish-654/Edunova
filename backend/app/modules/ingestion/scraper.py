"""Scraper engine.

Launches a headless Chromium via Playwright, fetches the target URL,
captures the rendered DOM, and stores the raw payload in the staging store.
Fetch failures produce an audit record in `ingestion_anomaly_logs`.
"""

import uuid

from playwright.async_api import async_playwright
from sqlalchemy import text

from app.core.database import AsyncSessionLocal

FETCH_TIMEOUT_MS = 30_000


async def run_scraper(source_id: uuid.UUID, target_url: str) -> None:
    """Crawl `target_url` and persist the raw payload to the staging store."""
    raw_html = ""
    validation_status = "PENDING"
    anomaly_type: str | None = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent=(
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                )
            )
            try:
                response = await page.goto(
                    target_url, wait_until="domcontentloaded", timeout=FETCH_TIMEOUT_MS
                )
                if response:
                    status = response.status
                else:
                    status = 599
                raw_html = await page.content()
                if status == 200:
                    validation_status = "PROCESSED"
                else:
                    validation_status = "FAILED"
                    anomaly_type = f"HTTP_ERROR:{status}"
            finally:
                await browser.close()
    except Exception as exc:  # network / navigation errors
        validation_status = "FAILED"
        anomaly_type = "CRAWL_EXCEPTION"

    await _store_payload(source_id, raw_html, validation_status, anomaly_type)


async def _store_payload(
    source_id: uuid.UUID,
    raw_html: str,
    validation_status: str,
    anomaly_type: str | None,
) -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                text(
                    """
                    INSERT INTO raw_staging_payloads (source_id, raw_html_or_json, is_processed)
                    VALUES (:source_id, :raw_html, :is_processed)
                    RETURNING payload_id;
                    """
                ),
                {
                    "source_id": source_id,
                    "raw_html": raw_html,
                    "is_processed": validation_status == "PROCESSED",
                },
            )
            payload_id = result.scalar()

            if validation_status == "FAILED" and payload_id:
                await session.execute(
                    text(
                        """
                        INSERT INTO ingestion_anomaly_logs (payload_id, error_code, missing_fields)
                        VALUES (:payload_id, :error_code, ARRAY[]::TEXT[]);
                        """
                    ),
                    {"payload_id": payload_id, "error_code": anomaly_type},
                )
        await session.commit()