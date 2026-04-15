from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

class CompetitorPolicy(Base):
  __tablename__ = "COMPETITOR_POLICIES"

  policy_id: Mapped[int] = mapped_column("POLICY_ID", BigInteger, Sequence("competitor_policies_policy_id_seq"), primary_key=True)
  competitor_id: Mapped[int] = mapped_column("COMPETITOR_ID", BigInteger, ForeignKey("COMPETITORS.COMPETITOR_ID"), nullable=False)
  policy_type_id: Mapped[int | None] = mapped_column("POLICY_TYPE_ID", BigInteger, ForeignKey("POLICY_TYPES.POLICY_TYPE_ID"), nullable=True)
  policy_date: Mapped[date] = mapped_column("POLICY_DATE", Date, nullable=False)
  policy_data: Mapped[dict[str, Any] | None] = mapped_column("POLICY_DATA", JSONB, nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  competitor: Mapped["Competitor"] = relationship("Competitor", back_populates="competitor_policies")
  policy_type: Mapped["PolicyType"] = relationship("PolicyType", back_populates="competitor_policies")
