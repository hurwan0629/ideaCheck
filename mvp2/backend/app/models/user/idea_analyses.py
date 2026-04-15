from enum import Enum
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Enum as SqlEnum, BigInteger, DateTime, ForeignKey, Sequence, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

class RecommendationType(str, Enum):
  GO = "GO"
  GO_WITH_CAUTION = "GO_WITH_CAUTION"
  PIVOT = "PIVOT"
  RETHINK = "RETHINK"

class IdeaAnalysis(Base):
  __tablename__ = "IDEA_ANALYSES"

  analysis_id: Mapped[int] = mapped_column("ANALYSIS_ID", BigInteger, Sequence("idea_analyses_analysis_id_seq"), primary_key=True)
  idea_id: Mapped[int] = mapped_column("IDEA_ID", BigInteger, ForeignKey("USER_IDEAS.IDEA_ID"), nullable=False, unique=True)
  recommendation_type: Mapped[RecommendationType] = mapped_column("RECOMMENDATION_TYPE", SqlEnum(RecommendationType), nullable=False)
  result_summary: Mapped[dict[str, Any] | None] = mapped_column("RESULT_SUMMARY", JSONB, nullable=True)
  result_raw: Mapped[str | None] = mapped_column("RESULT_RAW", Text, nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  user_idea: Mapped["UserIdea"] = relationship("UserIdea", back_populates="idea_analysis")
