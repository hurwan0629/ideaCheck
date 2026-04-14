from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

"""
Table COMPETITOR_ANALYSES {
  ANALYSIS_ID   bigint [pk]
  COMPETITOR_ID bigint [ref: > COMPETITORS.COMPETITOR_ID]
  ANALYSIS_DATE date        // 분석 기준일
  STRENGTH      jsonb       // AI 생성 강점 리스트
  WEAKNESS      jsonb       // AI 생성 약점 리스트
  CHARACTERISTIC jsonb      // 시장 포지셔닝 + 수치 (confidence 포함)
  CREATED_AT    timestamptz
}
"""

# 아이디어 매칭용 경쟁사 강/약점 참조 데이터.
# COMPETITOR_POLICIES (크롤링)와 달리 AI가 생성하는 분석 데이터.
# 변경 시 UPDATE 없이 새 행 추가. 최신 분석은 ANALYSIS_DATE DESC LIMIT 1 로 조회.
#
# STRENGTH / WEAKNESS 구조 예시:
# ["가격 경쟁력", "넓은 사용자층"]
#
# CHARACTERISTIC 구조 예시:
# {
#   "market_share": {
#     "estimated_pct": "10-20%",
#     "confidence": "low",          // low | medium | high
#     "basis": "앱 리뷰 수, 언론 노출 빈도 기반 추정"
#   },
#   "growth": {
#     "yoy_pct": null,              // 실수치 없으면 null
#     "trend": "up",                // up | flat | down
#     "confidence": "medium",
#     "basis": "최근 6개월 기사 빈도 증가"
#   },
#   "keywords": ["SaaS", "B2B", "중소기업"]
# }
# confidence가 low면 UI에서 "추정치" 라벨 표시. 실수치 데이터 확보 시 medium/high로 갱신.
class CompetitorAnalysis(Base):
  __tablename__ = "COMPETITOR_ANALYSES"

  analysis_id: Mapped[int] = mapped_column("ANALYSIS_ID", BigInteger, Sequence("competitor_analyses_analysis_id_seq"), primary_key=True)
  competitor_id: Mapped[int] = mapped_column("COMPETITOR_ID", BigInteger, ForeignKey("COMPETITORS.COMPETITOR_ID"), nullable=False)
  analysis_date: Mapped[date] = mapped_column("ANALYSIS_DATE", Date, nullable=False)
  strength: Mapped[list[Any] | None] = mapped_column("STRENGTH", JSONB, nullable=True)
  weakness: Mapped[list[Any] | None] = mapped_column("WEAKNESS", JSONB, nullable=True)
  characteristic: Mapped[dict[str, Any] | None] = mapped_column("CHARACTERISTIC", JSONB, nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  competitor: Mapped["Competitor"] = relationship("Competitor", back_populates="competitor_analyses")
