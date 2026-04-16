from enum import Enum
from datetime import datetime, timezone

from sqlalchemy import Enum as SqlEnum, BigInteger, String, Text, DateTime, Sequence
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship

from app.db import Base

class SourceType(str, Enum):
  NEWS = "NEWS"
  BLOG = "BLOG"
  REPORT = "REPORT"
  COMMUNITY = "COMMUNITY"
  ETC = "ETC"

class MarketRawSource(MappedAsDataclass, Base):
  __tablename__ = "MARKET_RAW_SOURCES"

  # default 없는 필드 먼저 (dataclass 규칙)
  title: Mapped[str] = mapped_column("TITLE", String(500), nullable=False)
  source_type: Mapped[SourceType] = mapped_column("SOURCE_TYPE", SqlEnum(SourceType), nullable=False)

  # default 있는 필드
  source_url: Mapped[str | None] = mapped_column("SOURCE_URL", Text, nullable=True, default=None)
  raw_content: Mapped[str | None] = mapped_column("RAW_CONTENT", Text, nullable=True, default=None)
  published_at: Mapped[datetime | None] = mapped_column("PUBLISHED_AT", DateTime(timezone=True), nullable=True, default=None)

  # 자동 생성 필드 (init=False → __init__ 인자에서 제외)
  raw_source_id: Mapped[int] = mapped_column("RAW_SOURCE_ID", BigInteger, Sequence("market_raw_sources_raw_source_id_seq"), primary_key=True, init=False)
  collected_at: Mapped[datetime] = mapped_column("COLLECTED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, init=False)

  market_extracts: Mapped[list["MarketExtract"]] = relationship("MarketExtract", back_populates="market_raw_source", default_factory=list, init=False)
