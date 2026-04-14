from enum import Enum
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Enum as SqlEnum, BigInteger, String, Text, DateTime, ForeignKey, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

"""
Table MARKET_EXTRACTS {
  EXTRACT_ID    bigint       [pk]
  RAW_SOURCE_ID bigint       [ref: > MARKET_RAW_SOURCES.RAW_SOURCE_ID]
  EXTRACT_TYPE  extract_type [not null]  // 추출 내용 유형
  TOPIC         varchar(255) [not null]  // 추출 주제
  PAIN_AREA     varchar(100)             // 불편함/문제 영역 (EXTRACT_TYPE = PAIN_POINT 일 때 주로 사용)
  SUMMARY       jsonb                    // AI가 추출한 핵심 요약
  EXTRACTED_DATA text                   // AI가 추출한 본문 발췌
  CREATED_AT    timestamptz  [not null]
}
"""

# EXTRACT_TYPE: 추출 결과의 성격 분류
# PAIN_POINT:    사회 문제 / 일상 불편함 — 창업자가 "이런 문제가 있구나" 발견하는 용도
# MARKET_SIZE:   시장 규모/성장률 수치 — 시장 크기 파악용
# STARTUP_CASE:  문제를 겨냥한 스타트업 사례 — "이미 이렇게 해결하려는 곳이 있다" 참고용
class ExtractType(str, Enum):
  PAIN_POINT = "PAIN_POINT"
  MARKET_SIZE = "MARKET_SIZE"
  STARTUP_CASE = "STARTUP_CASE"

# SUMMARY 구조 예시 (PAIN_POINT):
# {
#   "insight": "중소기업 사장의 67%가 세무 처리를 혼자 하며 월 평균 8시간 소요",
#   "keywords": ["세무", "중소기업", "자동화 니즈"],
#   "sentiment": "negative"  // 문제 상황이므로 negative
# }
#
# SUMMARY 구조 예시 (STARTUP_CASE):
# {
#   "company": "ㅇㅇ스타트업",
#   "problem_targeted": "소상공인 재고 관리",
#   "outcome": "Series A 50억 유치",
#   "keywords": ["소상공인", "재고", "B2B SaaS"]
# }
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
