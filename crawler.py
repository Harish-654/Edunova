from playwright.async_api import async_playwright
from sqlalchemy import text

from database import AsyncSessionLocal


async def run_scraper(source_id: int, target_url: str):
    """
    Asynchronously crawls target URL, writes raw payload to raw_staging_payloads,
    and logs anomaly errors if the fetch fails.
    """
    async with async_playwright() as p:
        # Launch browser context
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        raw_html = ""
        status_code = 500
        validation_status = "PENDING"
        anomaly_type = None
        error_desc = None

        try:
            response = await page.goto(
                target_url, wait_until="domcontentloaded", timeout=30000
            )
            if response:
                status_code = response.status
                raw_html = await page.content()
                if status_code == 200:
                    validation_status = "PROCESSED"
                else:
                    validation_status = "FAILED"
                    anomaly_type = "HTTP_ERROR"
                    error_desc = f"Server returned non-200 status: {status_code}"
        except Exception as e:
            validation_status = "FAILED"
            anomaly_type = "CRAWL_EXCEPTION"
            error_desc = str(e)
        finally:
            await browser.close()

        # Database Insertion
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # 1. Insert into raw staging payloads
                insert_payload_query = text("""
                    INSERT INTO raw_staging_payloads (source_id, raw_html_dom, http_status_code, validation_status)
                    VALUES (:source_id, :raw_html, :status_code, :validation_status)
                    RETURNING payload_id;
                """)
                result = await session.execute(
                    insert_payload_query,
                    {
                        "source_id": source_id,
                        "raw_html": raw_html,
                        "status_code": status_code,
                        "validation_status": validation_status,
                    },
                )
                payload_id = result.scalar()

                # 2. Log Anomaly if status failed
                if validation_status == "FAILED" and payload_id:
                    insert_anomaly_query = text("""
                        INSERT INTO ingestion_anomaly_logs (payload_id, anomaly_type, error_description)
                        VALUES (:payload_id, :anomaly_type, :error_desc);
                    """)
                    await session.execute(
                        insert_anomaly_query,
                        {
                            "payload_id": payload_id,
                            "anomaly_type": anomaly_type,
                            "error_desc": error_desc,
                        },
                    )
            await session.commit()
            print(
                f"[Crawler Finished] Source ID: {source_id} | Status: {validation_status}"
            )
