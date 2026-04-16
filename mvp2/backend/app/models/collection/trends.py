from enum import Enum
from datetime import date, datetime, timezone

from sqlalchemy import Enum as SqlEnum, BigInteger, String, Text, Date, DateTime, Numeric, Sequence
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column

from app.db import Base

class TopicType(str, Enum):
  SOCIAL = "SOCIAL"
  BUSINESS = "BUSINESS"
  TECH = "TECH"

class Trend(MappedAsDataclass, Base):
  __tablename__ = "TRENDS"

  # default 없는 필드 먼저 (dataclass 규칙)
  topic: Mapped[str] = mapped_column("TOPIC", String(255), nullable=False)
  topic_type: Mapped[TopicType] = mapped_column("TOPIC_TYPE", SqlEnum(TopicType), nullable=False)
  trend_date: Mapped[date] = mapped_column("TREND_DATE", Date, nullable=False)

  # default 있는 필드
  trend_score: Mapped[float | None] = mapped_column("TREND_SCORE", Numeric(10, 2), nullable=True, default=None)
  summary: Mapped[str | None] = mapped_column("SUMMARY", Text, nullable=True, default=None)
  source: Mapped[str | None] = mapped_column("SOURCE", String(255), nullable=True, default=None)

  # 자동 생성 필드 (init=False → __init__ 인자에서 제외)
  trend_id: Mapped[int] = mapped_column("TREND_ID", BigInteger, Sequence("trends_trend_id_seq"), primary_key=True, init=False)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, init=False)
