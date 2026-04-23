from enum import Enum
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Enum as SqlEnum, BigInteger, String, DateTime, ForeignKey, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db import Base

class IdeaStatus(str, Enum):
  DRAFT = "DRAFT"
  ACTIVE = "ACTIVE"
  ARCHIVED = "ARCHIVED"

# 사용자가 분석 요청한 아이디어.
# 린 캔버스 형태로 단계적으로 수집 (Step 1: title + core_idea 필수, 나머지 optional).
# 미입력 항목은 null로 저장, UI에서는 "고민중"으로 표시.
# 분석 시 AI가 null 항목에 대해 제안/보완 질문 제공.
#
# CONTENT 구조:
# {
#   "core_idea": "소상공인이 스마트폰으로 세금 신고를 쉽게 할 수 있는 앱",  // 필수
#   "target_customer": "자영업자, 소상공인",                                  // null 허용 = "고민중"
#   "business_model": "구독형 SaaS, 월 9,900원",                             // null 허용
#   "differentiation": "기존 프로그램 대비 모바일 중심, UI 단순화",           // null 허용
#   "problem_solved": "세무사 없이 혼자 신고하면 실수가 잦고 시간이 많이 걸림", // null 허용
#   "why_use_us": "국세청 연동 + AI 자동 계산으로 10분 안에 신고 완료",       // null 허용
#   "tags": ["세무", "소상공인", "B2B", "모바일"]
# }
class UserIdea(Base):
  __tablename__ = "USER_IDEAS"

  idea_id: Mapped[int] = mapped_column("IDEA_ID", BigInteger, Sequence("user_ideas_idea_id_seq"), primary_key=True)
  user_id: Mapped[int] = mapped_column("USER_ID", BigInteger, ForeignKey("USERS.USER_ID"), nullable=False)
  title: Mapped[str] = mapped_column("TITLE", String(255), nullable=False)
  content: Mapped[dict[str, Any]] = mapped_column("CONTENT", JSONB, nullable=False)
  status: Mapped[IdeaStatus] = mapped_column("STATUS", SqlEnum(IdeaStatus), nullable=False, default=IdeaStatus.DRAFT)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
  updated_at: Mapped[datetime] = mapped_column("UPDATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

  user: Mapped["User"] = relationship("User", back_populates="user_ideas")
  idea_analysis: Mapped["IdeaAnalysis"] = relationship("IdeaAnalysis", back_populates="user_idea", uselist=False)
