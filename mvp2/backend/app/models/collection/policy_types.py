from datetime import datetime, timezone

from sqlalchemy import BigInteger, String, Text, Boolean, DateTime, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

"""
Table POLICY_TYPES {
  POLICY_TYPE_ID bigint       [pk]
  NAME           varchar(100) [not null, unique]  // 정책 유형명 (예: "가격 정책", "현지화", "세대 겨냥")
  DESCRIPTION    text                             // 유형 설명
  IS_ACTIVE      boolean      [not null, default: true]  // false = 더 이상 신규 수집 안 함
  DEPRECATED_AT  timestamptz                      // IS_ACTIVE = false 로 바꾼 시점
  CREATED_AT     timestamptz  [not null]
}
"""

# 크롤러/AI가 COMPETITOR_POLICIES를 채울 때 참조하는 정책 유형 목록.
# 관리자 대시보드에서 추가/비활성화 가능.
# 절대 하드 DELETE 하지 않음 — is_active = false + deprecated_at 으로만 처리.
# 이유: 새로운 정책 유형은 계속 생겨나고, 오래된 유형은 히스토리로 보존해야 함
#   (예: "2년 전엔 세대 겨냥 마케팅이 유행했는데 지금은 사라짐" 같은 트렌드 분석 가능)
# 크롤러/AI는 WHERE is_active = true 조건으로만 참조해서 신규 데이터 생성.
class PolicyType(Base):
  __tablename__ = "POLICY_TYPES"

  policy_type_id: Mapped[int] = mapped_column("POLICY_TYPE_ID", BigInteger, Sequence("policy_types_policy_type_id_seq"), primary_key=True)
  name: Mapped[str] = mapped_column("NAME", String(100), nullable=False, unique=True)
  description: Mapped[str | None] = mapped_column("DESCRIPTION", Text, nullable=True)
  is_active: Mapped[bool] = mapped_column("IS_ACTIVE", Boolean, nullable=False, default=True)
  deprecated_at: Mapped[datetime | None] = mapped_column("DEPRECATED_AT", DateTime(timezone=True), nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  competitor_policies: Mapped[list["CompetitorPolicy"]] = relationship("CompetitorPolicy", back_populates="policy_type")
