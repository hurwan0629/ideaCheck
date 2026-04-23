from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import BIGINT, DateTime, ForeignKey, String, TEXT, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.core.database import Base

if TYPE_CHECKING:
  from common.models.idea import Idea

class AnalysisResult(Base):
  __tablename__ = "analysis_results"

  result_id: Mapped[int] = mapped_column("result_id", BIGINT, primary_key=True, init=False)
  idea_id: Mapped[int] = mapped_column(
    "idea_id",
    BIGINT,
    ForeignKey("ideas.idea_id"),
    nullable=False
  )
  raw_llm_response: Mapped[str] = mapped_column("raw_llm_response", TEXT, nullable=False)
  market_potential: Mapped[str] = mapped_column(
    "market_potential",
    String(20),
    nullable=False
  )
  result_json: Mapped[dict[str, Any] | list[Any]] = mapped_column(
    "result_json",
    JSONB,
    nullable=False
  )
  related_competitors_json: Mapped[list[Any] | None] = mapped_column(
    "related_competitors_json",
    JSONB,
    nullable=True,
    default=None
  )
  related_news_json: Mapped[list[Any] | None] = mapped_column(
    "related_news_json",
    JSONB,
    nullable=True,
    default=None
  )
  created_at: Mapped[datetime] = mapped_column(
    "created_at",
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False,
    init=False
  )

  idea: Mapped["Idea"] = relationship(
    back_populates="analysis_results",
    init=False
  )