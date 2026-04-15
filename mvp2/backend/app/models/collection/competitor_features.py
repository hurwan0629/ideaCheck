from datetime import datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db import Base

class CompetitorFeature(Base):
  __tablename__ = "COMPETITOR_FEATURES"

  feature_id: Mapped[int] = mapped_column("FEATURE_ID", BigInteger, Sequence("competitor_features_feature_id_seq"), primary_key=True)
  competitor_id: Mapped[int] = mapped_column("COMPETITOR_ID", BigInteger, ForeignKey("COMPETITORS.COMPETITOR_ID"), nullable=False)
  category_id: Mapped[int | None] = mapped_column("CATEGORY_ID", BigInteger, ForeignKey("FEATURE_CATEGORIES.CATEGORY_ID"), nullable=True)
  feature_name: Mapped[str] = mapped_column("FEATURE_NAME", String(255), nullable=False)
  feature_desc: Mapped[dict[str, Any] | None] = mapped_column("FEATURE_DESC", JSONB, nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  competitor: Mapped["Competitor"] = relationship("Competitor", back_populates="competitor_features")
  feature_category: Mapped["FeatureCategory"] = relationship("FeatureCategory", back_populates="competitor_features")
