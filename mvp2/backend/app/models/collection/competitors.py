from datetime import datetime, timezone

from sqlalchemy import BigInteger, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

"""
Table COMPETITORS {
  COMPETITOR_ID   bigint       [pk] // 경쟁사 PK
  NAME            varchar(255)      // 회사/서비스명
  TYPE            varchar(50)       // 업종 카테고리 (IT, 핀테크, 헬스케어 등)
  DESCRIPTION     text              // 서비스 한줄 설명
  TARGET_CUSTOMER text              // 타겟 고객군
  WEBSITE         varchar(255)      // 공식 사이트 (크롤링 출처 추적용)
  CREATED_AT      datetime
  UPDATED_AT      datetime
}
"""

# 기업 기본 정보 — 거의 안 바뀜. 바뀌면 UPDATE로 관리.
# TYPE은 업종이 늘어날 수 있어서 String으로 유연하게 관리
class Competitor(Base):
  __tablename__ = "COMPETITORS"

  competitor_id: Mapped[int] = mapped_column("COMPETITOR_ID", BigInteger, primary_key=True)
  name: Mapped[str] = mapped_column("NAME", String(255), nullable=False)
  type: Mapped[str] = mapped_column("TYPE", String(50), nullable=False)
  description: Mapped[str | None] = mapped_column("DESCRIPTION", Text, nullable=True)
  target_customer: Mapped[str | None] = mapped_column("TARGET_CUSTOMER", Text, nullable=True)
  website: Mapped[str | None] = mapped_column("WEBSITE", String(255), nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
  updated_at: Mapped[datetime] = mapped_column("UPDATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
