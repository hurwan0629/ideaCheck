from datetime import datetime, timezone

from sqlalchemy import BigInteger, String, Text, Boolean, DateTime, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

class FeatureCategory(Base):
  __tablename__ = "FEATURE_CATEGORIES"

  category_id: Mapped[int] = mapped_column("CATEGORY_ID", BigInteger, Sequence("feature_categories_category_id_seq"), primary_key=True)
  name: Mapped[str] = mapped_column("NAME", String(100), nullable=False, unique=True)
  description: Mapped[str | None] = mapped_column("DESCRIPTION", Text, nullable=True)
  is_active: Mapped[bool] = mapped_column("IS_ACTIVE", Boolean, nullable=False, default=True)
  deprecated_at: Mapped[datetime | None] = mapped_column("DEPRECATED_AT", DateTime(timezone=True), nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  competitor_features: Mapped[list["CompetitorFeature"]] = relationship("CompetitorFeature", back_populates="feature_category")
