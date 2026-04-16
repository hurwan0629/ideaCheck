from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship

from app.db import Base

class CompetitorPolicy(MappedAsDataclass, Base):
  __tablename__ = "COMPETITOR_POLICIES"

  # default 없는 필드 먼저 (dataclass 규칙)
  competitor_id: Mapped[int] = mapped_column("COMPETITOR_ID", BigInteger, ForeignKey("COMPETITORS.COMPETITOR_ID"), nullable=False)
  policy_date: Mapped[date] = mapped_column("POLICY_DATE", Date, nullable=False)

  # default 있는 필드
  policy_type_id: Mapped[int | None] = mapped_column("POLICY_TYPE_ID", BigInteger, ForeignKey("POLICY_TYPES.POLICY_TYPE_ID"), nullable=True, default=None)
  policy_data: Mapped[dict[str, Any] | None] = mapped_column("POLICY_DATA", JSONB, nullable=True, default=None)

  # 자동 생성 필드 (init=False → __init__ 인자에서 제외)
  policy_id: Mapped[int] = mapped_column("POLICY_ID", BigInteger, Sequence("competitor_policies_policy_id_seq"), primary_key=True, init=False)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, init=False)

  competitor: Mapped["Competitor"] = relationship("Competitor", back_populates="competitor_policies", init=False)
  policy_type: Mapped["PolicyType"] = relationship("PolicyType", back_populates="competitor_policies", init=False)
