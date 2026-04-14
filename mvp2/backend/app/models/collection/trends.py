from enum import Enum
from datetime import date, datetime, timezone

from sqlalchemy import Enum as SqlEnum, BigInteger, String, Text, Date, DateTime, Numeric, Sequence
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

"""
Table TRENDS {
  TREND_ID    bigint        [pk]
  TOPIC       varchar(255)  [not null]  // 트렌드 주제
  TOPIC_TYPE  topic_type    [not null]  // 주제 성격 분류
  TREND_DATE  date          [not null]  // 기준일
  TREND_SCORE decimal(10,2)             // 트렌드 점수 (source 내부 상대값, 직접 비교 불가)
  SUMMARY     text                      // 트렌드 요약
  SOURCE      varchar(255)              // 출처 (google_trends, naver_datalab 등)
  CREATED_AT  timestamptz   [not null]
}
"""

# RAW 테이블 없이 바로 저장하는 이유:
# Google Trends / 네이버 데이터랩 API에서 이미 정제된 점수값을 반환하기 때문.
#
# TOPIC_TYPE: 주제 성격 분류 — 나중에 창업자에게 "비즈니스 트렌드만 보기" 같은 필터 제공 가능
# SOCIAL:   쇼츠 유행, 밈, 소비 패턴 등 사회/문화적 트렌드
# BUSINESS: 산업 동향, 투자 트렌드, 규제 변화 등 비즈니스 트렌드
# TECH:     신기술, 개발 트렌드, AI/SaaS 등 기술 트렌드
#
# TREND_SCORE 주의: source별 내부 상대값 (0-100).
# Google Trends 88과 네이버 DataLab 88은 같은 의미가 아님.
# 시각화 시 source별로 분리해서 보여줄 것.
class TopicType(str, Enum):
  SOCIAL = "SOCIAL"
  BUSINESS = "BUSINESS"
  TECH = "TECH"

class Trend(Base):
  __tablename__ = "TRENDS"

  trend_id: Mapped[int] = mapped_column("TREND_ID", BigInteger, Sequence("trends_trend_id_seq"), primary_key=True)
  topic: Mapped[str] = mapped_column("TOPIC", String(255), nullable=False)
  topic_type: Mapped[TopicType] = mapped_column("TOPIC_TYPE", SqlEnum(TopicType), nullable=False)
  trend_date: Mapped[date] = mapped_column("TREND_DATE", Date, nullable=False)
  trend_score: Mapped[float | None] = mapped_column("TREND_SCORE", Numeric(10, 2), nullable=True)
  summary: Mapped[str | None] = mapped_column("SUMMARY", Text, nullable=True)
  source: Mapped[str | None] = mapped_column("SOURCE", String(255), nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
