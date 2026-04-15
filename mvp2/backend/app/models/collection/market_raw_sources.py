from enum import Enum
from datetime import datetime, timezone

from sqlalchemy import Enum as SqlEnum, BigInteger, String, Text, DateTime, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

class SourceType(str, Enum):
  NEWS = "NEWS"
  BLOG = "BLOG"
  REPORT = "REPORT"
  COMMUNITY = "COMMUNITY"
  ETC = "ETC"

class ContentType(str, Enum):
  PAIN_POINT = "PAIN_POINT"
  MARKET_DATA = "MARKET_DATA"
  STARTUP_STORY = "STARTUP_STORY"
  ETC = "ETC"

class MarketRawSource(Base):
  __tablename__ = "MARKET_RAW_SOURCES"

  raw_source_id: Mapped[int] = mapped_column("RAW_SOURCE_ID", BigInteger, Sequence("market_raw_sources_raw_source_id_seq"), primary_key=True)
  source_name: Mapped[str] = mapped_column("SOURCE_NAME", String(255), nullable=False)
  source_url: Mapped[str | None] = mapped_column("SOURCE_URL", Text, nullable=True)
  source_type: Mapped[SourceType] = mapped_column("SOURCE_TYPE", SqlEnum(SourceType), nullable=False)
  content_type: Mapped[ContentType] = mapped_column("CONTENT_TYPE", SqlEnum(ContentType), nullable=False)
  raw_content: Mapped[str | None] = mapped_column("RAW_CONTENT", Text, nullable=True)
  collected_at: Mapped[datetime] = mapped_column("COLLECTED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  market_extracts: Mapped[list["MarketExtract"]] = relationship("MarketExtract", back_populates="market_raw_source")
