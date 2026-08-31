from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from crawler import run_scraper
from database import get_db

app = FastAPI(title="EduNova Platform API", version="1.0.0")


# Request Models
class TriggerScrapeRequest(BaseModel):
    source_id: int
    target_url: HttpUrl


@app.get("/")
async def root():
    return {"message": "EduNova Backend Core Service is Running"}


# Route 1: Trigger Ingestion Crawler Background Task
@app.post("/api/v1/ingestion/trigger")
async def trigger_ingestion(
    payload: TriggerScrapeRequest, background_tasks: BackgroundTasks
):
    # Dispatch background crawler process without blocking API worker
    background_tasks.add_task(run_scraper, payload.source_id, str(payload.target_url))
    return {
        "status": "QUEUED",
        "message": f"Scrape job queued for source {payload.source_id}",
        "target_url": payload.target_url,
    }


# Route 2: Read Exams Catalog from Core Database
@app.get("/api/v1/exams")
async def get_exams(limit: int = 10, db: AsyncSession = Depends(get_db)):
    query = text(
        "SELECT exam_id, exam_name, conducting_body, official_url FROM exams LIMIT :limit;"
    )
    result = await db.execute(query, {"limit": limit})
    rows = result.fetchall()

    exams_list = [
        {
            "exam_id": str(row.exam_id),
            "exam_name": row.exam_name,
            "conducting_body": row.conducting_body,
            "official_url": row.official_url,
        }
        for row in rows
    ]
    return {"count": len(exams_list), "data": exams_list}


# Route 3: Read Anomaly Logs from Staging Pipeline
@app.get("/api/v1/ingestion/anomalies")
async def get_anomalies(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT log_id, payload_id, anomaly_type, error_description, flagged_at 
        FROM ingestion_anomaly_logs 
        ORDER BY flagged_at DESC LIMIT 20;
    """)
    result = await db.execute(query)
    rows = result.fetchall()

    anomalies = [
        {
            "log_id": row.log_id,
            "payload_id": str(row.payload_id),
            "anomaly_type": row.anomaly_type,
            "error_description": row.error_description,
            "flagged_at": row.flagged_at,
        }
        for row in rows
    ]
    return {"count": len(anomalies), "data": anomalies}
