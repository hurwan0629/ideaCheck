from datetime import date, datetime, timezone

from sqlalchemy import BigInteger, String, Text, Date, DateTime, Numeric, Sequence
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

"""
Table TRENDS {
  TREND_ID bigint [pk] // 트렌드 PK
  TOPIC varchar // 트렌드 주제
  TREND_DATE date // 기준일
  TREND_SCORE decimal // 트렌드 점수
  SUMMARY text // 요약
  SOURCE varchar // 출처
  CREATED_AT datetime // 생성일시
}
"""

# RAW 테이블을 안만든 이유는 GOOGLE TRENDS 또는 네이버 데이터랩 등에서 바로 정제된
# 데이ㅓ틀ㄹ 받기 때문에 그대로 갈 예정
class Trend(Base):
  __tablename__ = "TRENDS"

  trend_id: Mapped[int] = mapped_column("TREND_ID", BigInteger, Sequence("trends_trend_id_seq"), primary_key=True)
  topic: Mapped[str] = mapped_column("TOPIC", String(255), nullable=False)
  trend_date: Mapped[date] = mapped_column("TREND_DATE", Date, nullable=False)
  trend_score: Mapped[float | None] = mapped_column("TREND_SCORE", Numeric(10, 2), nullable=True)
  summary: Mapped[str | None] = mapped_column("SUMMARY", Text, nullable=True)
  source: Mapped[str | None] = mapped_column("SOURCE", String(255), nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)