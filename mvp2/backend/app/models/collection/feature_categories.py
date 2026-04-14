from datetime import datetime, timezone

from sqlalchemy import BigInteger, String, Text, Boolean, DateTime, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

"""
Table FEATURE_CATEGORIES {
  CATEGORY_ID    bigint       [pk]
  NAME           varchar(100) [not null, unique]  // 카테고리명 (예: "세무", "회계", "HR")
  DESCRIPTION    text                             // 카테고리 설명
  IS_ACTIVE      boolean      [not null, default: true]  // false = 더 이상 신규 수집 안 함
  DEPRECATED_AT  timestamptz                      // IS_ACTIVE = false 로 바꾼 시점
  CREATED_AT     timestamptz  [not null]
}
"""

# 크롤러/AI가 COMPETITOR_FEATURES를 채울 때 참조하는 카테고리 목록.
# 관리자 대시보드에서 추가/비활성화 가능.
# 절대 하드 DELETE 하지 않음 — is_active = false + deprecated_at 으로만 처리.
# 이유: COMPETITOR_FEATURES.CATEGORY_ID FK 참조 유지 + 히스토리 보존
class FeatureCategory(Base):
  __tablename__ = "FEATURE_CATEGORIES"

  category_id: Mapped[int] = mapped_column("CATEGORY_ID", BigInteger, Sequence("feature_categories_category_id_seq"), primary_key=True)
  name: Mapped[str] = mapped_column("NAME", String(100), nullable=False, unique=True)
  description: Mapped[str | None] = mapped_column("DESCRIPTION", Text, nullable=True)
  is_active: Mapped[bool] = mapped_column("IS_ACTIVE", Boolean, nullable=False, default=True)
  deprecated_at: Mapped[datetime | None] = mapped_column("DEPRECATED_AT", DateTime(timezone=True), nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  competitor_features: Mapped[list["CompetitorFeature"]] = relationship("CompetitorFeature", back_populates="feature_category")
