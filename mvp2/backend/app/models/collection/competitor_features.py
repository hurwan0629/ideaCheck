from datetime import datetime, timezone

from sqlalchemy import BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

"""
Table COMPETITOR_FEATURES {
  FEATURE_ID bigint [pk] // 경쟁사 기능 PK
  COMPETITOR_ID bigint [ref: > COMPETITORS.COMPETITOR_ID] // 경쟁사 FK
  FEATURE_NAME varchar // 기능명
  FEATURE_DESCRIPTION text // 기능 설명
  CREATED_AT datetime // 생성일시
}
"""

# 경쟁사의 자주 안바뀌는 기능 정보를 저장.
# 기능이 바뀌는 경우에는 새로운 데이터를 생성해서 저장
class CompetitorFeature(Base):
  __tablename__ = "COMPETITOR_FEATURES"

  feature_id: Mapped[int] = mapped_column("FEATURE_ID", BigInteger, primary_key=True)
  competitor_id: Mapped[int] = mapped_column("COMPETITOR_ID", BigInteger, ForeignKey("COMPETITORS.COMPETITOR_ID"), nullable=False)
  feature_name: Mapped[str] = mapped_column("FEATURE_NAME", String(255), nullable=False)
  feature_description: Mapped[str | None] = mapped_column("FEATURE_DESCRIPTION", Text, nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)