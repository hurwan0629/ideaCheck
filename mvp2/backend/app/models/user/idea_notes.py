from datetime import datetime, timezone
from typing import Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

"""
Table IDEA_NOTES {
  NOTE_ID bigint [pk] // 아이디어 노트 PK
  IDEA_ID bigint [ref: > USER_IDEAS.IDEA_ID] // 아이디어 FK
  USER_ID bigint [ref: > USERS.USER_ID] // 회원 FK
  TITLE varchar // 노트 제목
  CONTENT json // 노트 내용
  CREATED_AT datetime // 생성일시
  UPDATED_AT datetime // 수정일시
}
"""

class IdeaNote(Base):
  __tablename__ = "IDEA_NOTES"

  note_id: Mapped[int] = mapped_column("NOTE_ID", BigInteger, primary_key=True)
  idea_id: Mapped[int] = mapped_column("IDEA_ID", BigInteger, ForeignKey("USER_IDEAS.IDEA_ID"), nullable=False)
  user_id: Mapped[int] = mapped_column("USER_ID", BigInteger, ForeignKey("USERS.USER_ID"), nullable=False)
  title: Mapped[str] = mapped_column("TITLE", String(255), nullable=False)
  content: Mapped[dict[str, Any] | list[Any] | None] = mapped_column("CONTENT", JSONB, nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
  updated_at: Mapped[datetime] = mapped_column("UPDATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)