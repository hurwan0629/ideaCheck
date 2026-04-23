from common.core.database import Base
from datetime import datetime
from typing import Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BIGINT, func, TEXT, DateTime

class Competitor(Base):
  __tablename__="competitors"

  competitor_id: Mapped[int] = mapped_column("competitor_id", BIGINT, primary_key=True, init=False)
  name: Mapped[str] = mapped_column("name", String(255), nullable=False)
  category: Mapped[str] = mapped_column("category", String(100), nullable=False)
  business_model: Mapped[str] = mapped_column("business_model", String(100), nullable=False)
  target_market: Mapped[str] = mapped_column("target_market", String(255), nullable=False)
  feature_json: Mapped[dict[str, Any] | list[Any]] = mapped_column("feature_json", JSONB, nullable=False)
  source_url: Mapped[str] = mapped_column("source_url", String(255), nullable=False)
  summary: Mapped[str | None] = mapped_column("summary", TEXT, nullable=True, default=None)
  homepage_url: Mapped[str | None] = mapped_column("homepage_url", String(255), nullable=True, default=None)
  collected_at: Mapped[datetime] = mapped_column("collected_at", DateTime(timezone=True), server_default=func.now(), nullable=False, init=False)
  updated_at: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, init=False)


"""
able competitors {
  competitor_id bigint [pk, increment, note: 'Primary key for one competitor']
  name varchar(255) [not null, note: 'Competitor service or company name']
  category varchar(100) [not null, note: 'High-level category such as AI tool, education, SaaS']
  summary text [note: 'Short description of what the competitor does']
  homepage_url varchar(255) [note: 'Official homepage URL']
  business_model varchar(100) [note: 'Examples: B2B, B2C, SaaS, Marketplace']
  target_market varchar(255) [note: 'Main market or customer segment the competitor targets']
  feature_json jsonb [note: 'Flexible competitor details such as strengths, weaknesses, features']
  source_url varchar(255) [note: 'Source page used when collecting competitor data']
  collected_at timestamp [not null, note: 'When this competitor data was collected']
  updated_at timestamp [not null, note: 'When this competitor row was last updated']

  Note: '''
  competitors is a reference table used by the analyzer.

  feature_json example:
  {
    "strengths": [],
    "weaknesses": [],
    "features": [],
    "notes": ""
  }
  '''
}
"""
