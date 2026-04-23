from datetime import date, datetime, timezone

from sqlalchemy import BigInteger, String, Date, DateTime, Sequence
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

class IdeaTopicStats(Base):
  __tablename__ = "IDEA_TOPIC_STATS"

  idea_topic_stat_id: Mapped[int] = mapped_column("STAT_ID", BigInteger, Sequence("idea_topic_stats_stat_id_seq"), primary_key=True)
  stat_date: Mapped[date] = mapped_column("STAT_DATE", Date, nullable=False)
  topic: Mapped[str] = mapped_column("TOPIC", String(255), nullable=False)
  idea_count: Mapped[int] = mapped_column("IDEA_COUNT", BigInteger, nullable=False, default=0)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)