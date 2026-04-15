from datetime import datetime, timezone

from sqlalchemy import BigInteger, String, Text, DateTime, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

class Competitor(Base):
  __tablename__ = "COMPETITORS"

  competitor_id: Mapped[int] = mapped_column("COMPETITOR_ID", BigInteger, Sequence("competitors_competitor_id_seq"), primary_key=True)
  name: Mapped[str] = mapped_column("NAME", String(255), nullable=False)
  type: Mapped[str] = mapped_column("TYPE", String(50), nullable=False)
  description: Mapped[str | None] = mapped_column("DESCRIPTION", Text, nullable=True)
  target_customer: Mapped[str | None] = mapped_column("TARGET_CUSTOMER", Text, nullable=True)
  website: Mapped[str | None] = mapped_column("WEBSITE", String(255), nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
  updated_at: Mapped[datetime] = mapped_column("UPDATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

  competitor_analyses: Mapped[list["CompetitorAnalysis"]] = relationship("CompetitorAnalysis", back_populates="competitor")
  competitor_features: Mapped[list["CompetitorFeature"]] = relationship("CompetitorFeature", back_populates="competitor")
  competitor_policies: Mapped[list["CompetitorPolicy"]] = relationship("CompetitorPolicy", back_populates="competitor")
