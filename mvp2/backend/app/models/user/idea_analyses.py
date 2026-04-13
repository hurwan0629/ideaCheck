from datetime import datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, Sequence, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

"""
Table IDEA_ANALYSES {
  ANALYSIS_ID    bigint [pk] // 아이디어 분석 PK
  IDEA_ID        bigint [ref: > USER_IDEAS.IDEA_ID] // 아이디어 FK
  RESULT_SUMMARY jsonb       // 분석 요약 + 매칭된 경쟁사 리스트
  RESULT_RAW     text        // AI 분석 원문
  CREATED_AT     datetime
}
"""

# 아이디어 1개당 행 1개.
# 경쟁사 분석은 COMPETITOR_ANALYSES에 사전 저장된 데이터를 참조하여 생성.
#
# RESULT_SUMMARY 구조 예시:
# {
#   "direction": "B2B SaaS 틈새시장 공략",
#   "differentiation": ["모바일 우선 UX", "저가 진입 전략"],
#   "matched_competitors": [100, 101, 102]  // COMPETITOR_ANALYSES.COMPETITOR_ID
# }
class IdeaAnalysis(Base):
  __tablename__ = "IDEA_ANALYSES"

  analysis_id: Mapped[int] = mapped_column("ANALYSIS_ID", BigInteger, Sequence("idea_analyses_analysis_id_seq"), primary_key=True)
  idea_id: Mapped[int] = mapped_column("IDEA_ID", BigInteger, ForeignKey("USER_IDEAS.IDEA_ID"), nullable=False)
  result_summary: Mapped[dict[str, Any] | None] = mapped_column("RESULT_SUMMARY", JSONB, nullable=True)
  result_raw: Mapped[str | None] = mapped_column("RESULT_RAW", Text, nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  user_idea: Mapped["UserIdea"] = relationship("UserIdea", back_populates="idea_analysis")
