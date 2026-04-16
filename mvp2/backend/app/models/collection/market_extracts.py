from enum import Enum
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Enum as SqlEnum, BigInteger, String, DateTime, ForeignKey, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship

from app.db import Base

class ExtractType(str, Enum):
  PAIN_POINT = "PAIN_POINT"
  MARKET_SIZE = "MARKET_SIZE"
  STARTUP_CASE = "STARTUP_CASE"

class MarketExtract(MappedAsDataclass, Base):
  __tablename__ = "MARKET_EXTRACTS"

  # default 없는 필드 먼저 (dataclass 규칙)
  raw_source_id: Mapped[int] = mapped_column("RAW_SOURCE_ID", BigInteger, ForeignKey("MARKET_RAW_SOURCES.RAW_SOURCE_ID"), nullable=False)
  # PAIN_POINT / MARKET_SIZE / STARTUP_CASE 중 ai가 판별
  extract_type: Mapped[ExtractType] = mapped_column("EXTRACT_TYPE", SqlEnum(ExtractType), nullable=False)
  # ai가 분석한 주제
  topic: Mapped[str] = mapped_column("TOPIC", String(255), nullable=False)

  # default 있는 필드
  # TYPE가 PAIN_POINT면 작성, 없으면 NULL
  pain_area: Mapped[str | None] = mapped_column("PAIN_AREA", String(100), nullable=True, default=None)
  # 분석된 정보들 (JSONㅠ)
  extracted_data: Mapped[dict[str, Any] | None] = mapped_column("EXTRACTED_DATA", JSONB, nullable=True, default=None)

  # 자동 생성 필드 (init=False → __init__ 인자에서 제외)
  extract_id: Mapped[int] = mapped_column("EXTRACT_ID", BigInteger, Sequence("market_extracts_extract_id_seq"), primary_key=True, init=False)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, init=False)

  market_raw_source: Mapped["MarketRawSource"] = relationship("MarketRawSource", back_populates="market_extracts", init=False)
