from datetime import datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db import Base

"""
Table COMPETITOR_FEATURES {
  FEATURE_ID    bigint       [pk]
  COMPETITOR_ID bigint       [ref: > COMPETITORS.COMPETITOR_ID]
  CATEGORY_ID   bigint       [ref: > FEATURE_CATEGORIES.CATEGORY_ID]  // 기능 카테고리 FK
  FEATURE_NAME  varchar(255) [not null]                                // 기능명
  FEATURE_DESC  jsonb                                                  // 기능 상세
  CREATED_AT    timestamptz  [not null]
}
"""

# 경쟁사의 주요 기능 정보를 저장.
# CATEGORY_ID: FEATURE_CATEGORIES 테이블에서 관리. is_active = true 인 카테고리만 신규 수집 시 사용.
# 변경 시 UPDATE 없이 새 행 추가 (이력 보존).
#
# FEATURE_DESC 구조 예시:
# {
#   "description": "세금 신고서를 자동으로 작성하고 제출합니다",
#   "detail": "국세청 API 연동, 부가세/소득세 지원"
# }
class CompetitorFeature(Base):
  __tablename__ = "COMPETITOR_FEATURES"

  feature_id: Mapped[int] = mapped_column("FEATURE_ID", BigInteger, Sequence("competitor_features_feature_id_seq"), primary_key=True)
  competitor_id: Mapped[int] = mapped_column("COMPETITOR_ID", BigInteger, ForeignKey("COMPETITORS.COMPETITOR_ID"), nullable=False)
  category_id: Mapped[int | None] = mapped_column("CATEGORY_ID", BigInteger, ForeignKey("FEATURE_CATEGORIES.CATEGORY_ID"), nullable=True)
  feature_name: Mapped[str] = mapped_column("FEATURE_NAME", String(255), nullable=False)
  feature_desc: Mapped[dict[str, Any] | None] = mapped_column("FEATURE_DESC", JSONB, nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  competitor: Mapped["Competitor"] = relationship("Competitor", back_populates="competitor_features")
  feature_category: Mapped["FeatureCategory"] = relationship("FeatureCategory", back_populates="competitor_features")
