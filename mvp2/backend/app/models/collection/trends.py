from enum import Enum
from datetime import date, datetime, timezone

from sqlalchemy import Enum as SqlEnum, BigInteger, String, Text, Date, DateTime, Numeric, Sequence
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

class TopicType(str, Enum):
  SOCIAL = "SOCIAL"
  BUSINESS = "BUSINESS"
  TECH = "TECH"

class Trend(Base):
  __tablename__ = "TRENDS"

  trend_id: Mapped[int] = mapped_column("TREND_ID", BigInteger, Sequence("trends_trend_id_seq"), primary_key=True)
  topic: Mapped[str] = mapped_column("TOPIC", String(255), nullable=False)
  topic_type: Mapped[TopicType] = mapped_column("TOPIC_TYPE", SqlEnum(TopicType), nullable=False)
  trend_date: Mapped[date] = mapped_column("TREND_DATE", Date, nullable=False)
  trend_score: Mapped[float | None] = mapped_column("TREND_SCORE", Numeric(10, 2), nullable=True)
  summary: Mapped[str | None] = mapped_column("SUMMARY", Text, nullable=True)
  source: Mapped[str | None] = mapped_column("SOURCE", String(255), nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
