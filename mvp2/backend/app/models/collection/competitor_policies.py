from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

"""
Table COMPETITOR_POLICIES {
  POLICY_ID      bigint [pk]
  COMPETITOR_ID  bigint [ref: > COMPETITORS.COMPETITOR_ID]
  POLICY_TYPE_ID bigint [ref: > POLICY_TYPES.POLICY_TYPE_ID]  // 정책 유형 FK
  POLICY_DATE    date        // 정책 기준일 (기업이 발표한 날짜)
  POLICY_DATA    jsonb       // 해당 유형에 맞는 세부 내용
  CREATED_AT     timestamptz // 수집일시
}
"""

# 시기마다 바뀌는 정책/포지셔닝 이력을 저장.
# POLICY_TYPE_ID: POLICY_TYPES 테이블에서 관리. is_active = true 인 유형만 신규 수집 시 사용.
# POLICY_DATE: 기업이 해당 정책을 발표/적용한 날짜.
# CREATED_AT:  우리가 해당 정보를 수집/크롤링한 날짜.
# 변경 시 UPDATE 없이 새 행 추가 (이력 보존).
#
# POLICY_DATA 구조 예시 (유형별로 다름):
# 가격 정책: { "tier": "freemium", "base_price": "월 9,900원", "enterprise": "문의" }
# 현지화:   { "target_region": "동남아", "language": ["ko", "en", "vi"] }
# 세대 겨냥: { "target_generation": "MZ", "channel": "인스타그램", "message": "..." }
class CompetitorPolicy(Base):
  __tablename__ = "COMPETITOR_POLICIES"

  policy_id: Mapped[int] = mapped_column("POLICY_ID", BigInteger, Sequence("competitor_policies_policy_id_seq"), primary_key=True)
  competitor_id: Mapped[int] = mapped_column("COMPETITOR_ID", BigInteger, ForeignKey("COMPETITORS.COMPETITOR_ID"), nullable=False)
  policy_type_id: Mapped[int | None] = mapped_column("POLICY_TYPE_ID", BigInteger, ForeignKey("POLICY_TYPES.POLICY_TYPE_ID"), nullable=True)
  policy_date: Mapped[date] = mapped_column("POLICY_DATE", Date, nullable=False)
  policy_data: Mapped[dict[str, Any] | None] = mapped_column("POLICY_DATA", JSONB, nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  competitor: Mapped["Competitor"] = relationship("Competitor", back_populates="competitor_policies")
  policy_type: Mapped["PolicyType"] = relationship("PolicyType", back_populates="competitor_policies")
