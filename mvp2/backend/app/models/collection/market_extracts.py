from datetime import datetime, timezone
from typing import Any
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

"""
Table MARKET_EXTRACTS {
  EXTRACT_ID bigint [pk] // 정제 데이터 PK
  RAW_SOURCE_ID bigint [ref: > MARKET_RAW_SOURCES.RAW_SOURCE_ID] // 원본 FK
  TOPIC varchar // 추출 주제
  SUMMARY json // 정제 요약
  EXTRACTED_DATA text // 추출 결과
  CREATED_AT datetime // 생성일시
}
"""

class MarketExtract(Base):
  __tablename__ = "MARKET_EXTRACTS"

  extract_id: Mapped[int] = mapped_column("EXTRACT_ID", BigInteger, primary_key=True)
  raw_source_id: Mapped[int] = mapped_column("RAW_SOURCE_ID", BigInteger, ForeignKey("MARKET_RAW_SOURCES.RAW_SOURCE_ID"), nullable=False)
  topic: Mapped[str] = mapped_column("TOPIC", String(255), nullable=False)
  summary: Mapped[dict[str, Any] | None] = mapped_column("SUMMARY", JSONB, nullable=True)
  extracted_data: Mapped[str | None] = mapped_column("EXTRACTED_DATA", Text, nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)