from enum import Enum
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Enum as SqlEnum, BigInteger, String, Text, DateTime, ForeignKey, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

class ExtractType(str, Enum):
  PAIN_POINT = "PAIN_POINT"
  MARKET_SIZE = "MARKET_SIZE"
  STARTUP_CASE = "STARTUP_CASE"

class MarketExtract(Base):
  __tablename__ = "MARKET_EXTRACTS"

  extract_id: Mapped[int] = mapped_column("EXTRACT_ID", BigInteger, Sequence("market_extracts_extract_id_seq"), primary_key=True)
  raw_source_id: Mapped[int] = mapped_column("RAW_SOURCE_ID", BigInteger, ForeignKey("MARKET_RAW_SOURCES.RAW_SOURCE_ID"), nullable=False)
  extract_type: Mapped[ExtractType] = mapped_column("EXTRACT_TYPE", SqlEnum(ExtractType), nullable=False)
  topic: Mapped[str] = mapped_column("TOPIC", String(255), nullable=False)
  pain_area: Mapped[str | None] = mapped_column("PAIN_AREA", String(100), nullable=True)
  summary: Mapped[dict[str, Any] | None] = mapped_column("SUMMARY", JSONB, nullable=True)
  extracted_data: Mapped[str | None] = mapped_column("EXTRACTED_DATA", Text, nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  market_raw_source: Mapped["MarketRawSource"] = relationship("MarketRawSource", back_populates="market_extracts")
