from enum import Enum
from datetime import datetime, timezone

from sqlalchemy import Enum as SqlEnum, BigInteger, String, Text, DateTime, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

"""
Table MARKET_RAW_SOURCES {
  RAW_SOURCE_ID bigint      [pk]
  SOURCE_NAME   varchar(255) [not null]  // 출처명
  SOURCE_URL    text                     // 원본 링크
  SOURCE_TYPE   source_type  [not null]  // 뉴스, 블로그, 리포트 등 (수집 매체 분류)
  CONTENT_TYPE  content_type [not null]  // 수집 내용 성격 분류
  RAW_CONTENT   text                     // 수집 원문
  COLLECTED_AT  timestamptz  [not null]
}
"""

# SOURCE_TYPE: 수집 매체 분류 (어디서 가져왔는가)
# 정제 단계에서 신뢰도 가중치를 다르게 주거나 특정 매체만 필터링할 때 사용
class SourceType(str, Enum):
  NEWS = "NEWS"
  BLOG = "BLOG"
  REPORT = "REPORT"
  COMMUNITY = "COMMUNITY"
  ETC = "ETC"

# CONTENT_TYPE: 수집 내용 성격 분류 (무슨 내용인가)
# PAIN_POINT:    사회 문제, 일상 불편함, 미해결 니즈를 다루는 기사/글
# MARKET_DATA:   시장 규모, 성장률 등 수치 중심 정보
# STARTUP_STORY: 특정 문제를 겨냥한 스타트업 사례 및 성공/실패 스토리
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
