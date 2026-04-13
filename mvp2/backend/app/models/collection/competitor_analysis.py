from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

"""
Table COMPETITOR_ANALYSIS {
  ANALYSIS_ID     bigint [pk] // 경쟁사 분석 PK
  COMPETITOR_ID   bigint [ref: > COMPETITORS.COMPETITOR_ID] // 경쟁사 FK
  ANALYSIS_DATE   date        // 분석 기준일
  STRENGTHS       jsonb       // ["가격 경쟁력", "넓은 사용자층"]
  WEAKNESSES      jsonb       // ["느린 업데이트", "모바일 UX 약함"]
  CHARACTERISTICS jsonb       // {"market_share": "중위권", "growth": "성장중", "keywords": [...]}
  CREATED_AT      datetime
}
"""

# 아이디어 매칭용 경쟁사 강/약점 참조 데이터.
# COMPETITOR_POLICIES (사람이 수집/크롤링) 와 달리 AI가 생성하는 분석 데이터.
# 변경 시 UPDATE 없이 새 행 추가. 최신 분석은 ANALYSIS_DATE DESC LIMIT 1 로 조회.
class CompetitorAnalysis(Base):
  __tablename__ = "COMPETITOR_ANALYSIS"

  analysis_id: Mapped[int] = mapped_column("ANALYSIS_ID", BigInteger, Sequence("competitor_analysis_analysis_id_seq"), primary_key=True)
  competitor_id: Mapped[int] = mapped_column("COMPETITOR_ID", BigInteger, ForeignKey("COMPETITORS.COMPETITOR_ID"), nullable=False)
  analysis_date: Mapped[date] = mapped_column("ANALYSIS_DATE", Date, nullable=False)
  strengths: Mapped[list[Any] | None] = mapped_column("STRENGTHS", JSONB, nullable=True)
  weaknesses: Mapped[list[Any] | None] = mapped_column("WEAKNESSES", JSONB, nullable=True)
  characteristics: Mapped[dict[str, Any] | None] = mapped_column("CHARACTERISTICS", JSONB, nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  competitor: Mapped["Competitor"] = relationship("Competitor", back_populates="competitor_analyses")
