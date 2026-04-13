from enum import Enum
from datetime import datetime, timezone

from sqlalchemy import Enum as SqlEnum, BigInteger, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

"""
Table MARKET_RAW_SOURCES {
  RAW_SOURCE_ID bigint [pk] // 시장정보 원본 PK
  SOURCE_NAME varchar // 출처명
  SOURCE_URL text // 원본 링크
  SOURCE_TYPE varchar // 뉴스, 블로그, 리포트 등
  RAW_CONTENT text // 수집 원문
  COLLECTED_AT datetime // 수집일시
}
"""

# 이거 왜 하는거임?
# 정제 단계에서 신뢰도 가중치를 다르게 주거나 특정 타입만 필터링할 때 사용 가능
class SourceType(str, Enum):
  NEWS = "NEWS"
  BLOG = "BLOG"
  REPORT = "REPORT"
  COMMUNITY = "COMMUNITY"
  ETC = "ETC"

class MarketRawSource(Base):
  __tablename__ = "MARKET_RAW_SOURCES"

  raw_source_id: Mapped[int] = mapped_column("RAW_SOURCE_ID", BigInteger, primary_key=True)
  source_name: Mapped[str] = mapped_column("SOURCE_NAME", String(255), nullable=False)
  source_url: Mapped[str | None] = mapped_column("SOURCE_URL", Text, nullable=True)
  source_type: Mapped[SourceType] = mapped_column("SOURCE_TYPE", SqlEnum(SourceType), nullable=False)
  raw_content: Mapped[str | None] = mapped_column("RAW_CONTENT", Text, nullable=True)
  collected_at: Mapped[datetime] = mapped_column("COLLECTED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)