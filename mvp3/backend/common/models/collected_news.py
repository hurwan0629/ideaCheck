from datetime import datetime

from sqlalchemy import BIGINT, DateTime, String, TEXT, func
from sqlalchemy.orm import Mapped, mapped_column

from common.core.database import Base


class CollectedNews(Base):
  __tablename__ = "collected_news"

  news_id: Mapped[int] = mapped_column("news_id", BIGINT, primary_key=True, init=False)
  title: Mapped[str] = mapped_column("title", String(255), nullable=False)
  source_name: Mapped[str] = mapped_column("source_name", String(100), nullable=False)
  url: Mapped[str] = mapped_column("url", String(255), nullable=False, unique=True)
  published_at: Mapped[datetime] = mapped_column(
    "published_at",
    DateTime(timezone=True),
    nullable=False
  )
  content: Mapped[str] = mapped_column("content", TEXT, nullable=False)
  summary: Mapped[str | None] = mapped_column("summary", TEXT, nullable=True, default=None)
  category: Mapped[str | None] = mapped_column("category", String(100), nullable=True, default=None)
  collected_at: Mapped[datetime] = mapped_column(
    "collected_at",
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False,
    init=False
  )
