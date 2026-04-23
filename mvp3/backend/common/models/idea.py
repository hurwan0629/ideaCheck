from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BIGINT, String, TEXT, DateTime, func
from common.core.database import Base

from datetime import datetime
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
  from common.models.analysis_result import AnalysisResult

class Idea(Base):
  __tablename__="ideas"

  idea_id: Mapped[int] = mapped_column("idea_id", BIGINT, primary_key=True, init=False)
  nickname: Mapped[str] = mapped_column("nickname", String(50), nullable=False)
  title: Mapped[str] = mapped_column("title", String(255), nullable=False)
  problem: Mapped[str] = mapped_column("problem", TEXT, nullable=False)
  solution_summary: Mapped[str] = mapped_column("solution_summary", TEXT, nullable=False)
  raw_input_json: Mapped[dict[str, Any] | list[Any]] = mapped_column(
    "raw_input_json", JSONB, nullable=False,
  )
  email: Mapped[str | None] = mapped_column(
    "email", String(100), nullable=True,
    default=None
  )
  target_user: Mapped[str | None] = mapped_column(
    "target_user", TEXT, nullable=True,
    default=None
  )
  created_at: Mapped[datetime] = mapped_column(
    "created_at", DateTime(timezone=True), 
    server_default=func.now(), nullable=False,
    init=False
  )
  updated_at: Mapped[datetime] = mapped_column(
    "updated_at", DateTime(timezone=True), 
    server_default=func.now(), onupdate=func.now(), nullable=False,
    init=False
  )

  analysis_results: Mapped[list["AnalysisResult"]] = relationship(
    back_populates="idea",
    default_factory=list,
    init=False
  )

"""
raw_input_json example:
  {
    "idea_background": "",
    "expected_users": [],
    "pain_points": [],
    "reference_services": [],
    "additional_notes": ""
  }
"""