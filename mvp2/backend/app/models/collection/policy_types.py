from datetime import datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, String, Text, Boolean, DateTime, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

class PolicyType(Base):
  __tablename__ = "POLICY_TYPES"

  policy_type_id: Mapped[int] = mapped_column("POLICY_TYPE_ID", BigInteger, Sequence("policy_types_policy_type_id_seq"), primary_key=True)
  name: Mapped[str] = mapped_column("NAME", String(100), nullable=False, unique=True)
  description: Mapped[str | None] = mapped_column("DESCRIPTION", Text, nullable=True)
  policy_props: Mapped[list[Any] | None] = mapped_column("POLICY_PROPS", JSONB, nullable=True)
  is_active: Mapped[bool] = mapped_column("IS_ACTIVE", Boolean, nullable=False, default=True)
  deprecated_at: Mapped[datetime | None] = mapped_column("DEPRECATED_AT", DateTime(timezone=True), nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  competitor_policies: Mapped[list["CompetitorPolicy"]] = relationship("CompetitorPolicy", back_populates="policy_type")
