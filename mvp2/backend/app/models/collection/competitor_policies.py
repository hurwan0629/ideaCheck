from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

"""
Table COMPETITOR_POLICIES {
  POLICY_ID     bigint [pk] // 경쟁사 시점별 정책 PK
  COMPETITOR_ID bigint [ref: > COMPETITORS.COMPETITOR_ID] // 경쟁사 FK
  POLICY_DATE   date        // 정책 기준일 (기업이 발표한 날짜)
  POLICY_DATA   jsonb       // {"price": {...}, "positioning": "...", "strategy": "..."}
  CREATED_AT    datetime    // 수집일시 (크롤링한 날짜)
}
"""

# 시기마다 바뀌는 정책/포지셔닝 이력을 저장
# POLICY_DATE: 기업이 해당 정책을 발표/적용한 날짜
# CREATED_AT:  우리가 해당 정보를 수집/크롤링한 날짜
# 변경 시 UPDATE 없이 새 행 추가 (이력 보존)
#
# POLICY_DATA 구조 예시:
# {
#   "price": {"tier": "freemium", "base_price": "월 9,900원"},
#   "positioning": "중소기업 타겟 올인원 SaaS",
#   "strategy": "가격 경쟁력으로 대기업 제품 대체"
# }
class CompetitorPolicy(Base):
  __tablename__ = "COMPETITOR_POLICIES"

  policy_id: Mapped[int] = mapped_column("POLICY_ID", BigInteger, primary_key=True)
  competitor_id: Mapped[int] = mapped_column("COMPETITOR_ID", BigInteger, ForeignKey("COMPETITORS.COMPETITOR_ID"), nullable=False)
  policy_date: Mapped[date] = mapped_column("POLICY_DATE", Date, nullable=False)
  policy_data: Mapped[dict[str, Any] | None] = mapped_column("POLICY_DATA", JSONB, nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
