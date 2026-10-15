import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ScrapingSource(Base):
    __tablename__ = "scraping_sources"

    source_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    target_name: Mapped[str] = mapped_column(String(255))
    target_url: Mapped[str] = mapped_column(String(500))
    cron_expression: Mapped[str | None] = mapped_column(String(50), default="0 0 * * *")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class RawStagingPayload(Base):
    __tablename__ = "raw_staging_payloads"

    payload_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("scraping_sources.source_id", ondelete="CASCADE")
    )
    raw_html_or_json: Mapped[str] = mapped_column(Text)
    fetched_at: Mapped[datetime] = mapped_column(server_default=func.now())
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)


class IngestionAnomalyLog(Base):
    __tablename__ = "ingestion_anomaly_logs"

    log_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    payload_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("raw_staging_payloads.payload_id", ondelete="CASCADE")
    )
    error_code: Mapped[str] = mapped_column(String(100))
    missing_fields: Mapped[list[str] | None] = mapped_column(ARRAY(Text), default=None)
    logged_at: Mapped[datetime] = mapped_column(server_default=func.now())
