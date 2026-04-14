from enum import Enum
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Enum as SqlEnum, BigInteger, DateTime, ForeignKey, Sequence, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

"""
Table IDEA_ANALYSES {
  ANALYSIS_ID       bigint              [pk]
  IDEA_ID           bigint              [ref: - USER_IDEAS.IDEA_ID]  // 1:1
  RECOMMENDATION_TYPE recommendation_type [not null]                 // 진입 판단 결과
  RESULT_SUMMARY    jsonb                                            // 분석 요약 + 매칭 경쟁사
  RESULT_RAW        text                                             // AI 분석 원문
  CREATED_AT        timestamptz         [not null]
}
"""

# 아이디어 1개당 행 1개.
# 경쟁사 분석은 COMPETITOR_ANALYSES에 사전 저장된 데이터를 RAG로 참조하여 생성.
#
# RECOMMENDATION_TYPE: UI에서 색상/아이콘 분기용
# GO:              진입 가능, 차별화 포인트 유효
# GO_WITH_CAUTION: 진입 가능하나 리스크 존재 — 리스크 완화 방법 제시
# PIVOT:           현재 방향은 어렵지만 다른 방향으로 틀면 가능 — 구체적 전환 방향 제시
# RETHINK:         근본적으로 재검토 필요 — 왜 안되는지 + 어떤 부분을 바꿔야 하는지 제시
class RecommendationType(str, Enum):
  GO = "GO"
  GO_WITH_CAUTION = "GO_WITH_CAUTION"
  PIVOT = "PIVOT"
  RETHINK = "RETHINK"

# RESULT_SUMMARY 구조:
# {
#   "entry_feasibility_score": 72,           // 0-100, AI가 근거 기반 생성
#   "direction": "B2B SaaS 틈새시장 공략",
#   "differentiation": [
#     { "point": "모바일 우선 UX", "valid": true, "reason": "기존 경쟁사 모두 데스크탑 중심" }
#   ],
#   "matched_competitors": [
#     { "id": 100, "similarity": 0.87, "reason": "세무 자동화 기능과 타겟 고객군 유사" }
#   ],
#   "risks": ["기존 세무사 시장과의 채널 충돌"],
#   "suggestions": ["초기 타겟을 1인 사업자로 좁혀 진입 후 확장"],
#   "market_context": ["세무 자동화 SaaS 시장 연 38% 성장 추정"]  // MARKET_EXTRACTS 기반
# }
class IdeaAnalysis(Base):
  __tablename__ = "IDEA_ANALYSES"

  analysis_id: Mapped[int] = mapped_column("ANALYSIS_ID", BigInteger, Sequence("idea_analyses_analysis_id_seq"), primary_key=True)
  idea_id: Mapped[int] = mapped_column("IDEA_ID", BigInteger, ForeignKey("USER_IDEAS.IDEA_ID"), nullable=False, unique=True)
  recommendation_type: Mapped[RecommendationType] = mapped_column("RECOMMENDATION_TYPE", SqlEnum(RecommendationType), nullable=False)
  result_summary: Mapped[dict[str, Any] | None] = mapped_column("RESULT_SUMMARY", JSONB, nullable=True)
  result_raw: Mapped[str | None] = mapped_column("RESULT_RAW", Text, nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  user_idea: Mapped["UserIdea"] = relationship("UserIdea", back_populates="idea_analysis")
