from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

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
