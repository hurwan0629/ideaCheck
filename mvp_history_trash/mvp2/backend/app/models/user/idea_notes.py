from datetime import datetime, timezone
from typing import Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import BigInteger, String, DateTime, Sequence, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

class IdeaNote(Base):
  __tablename__ = "IDEA_NOTES"

  note_id: Mapped[int] = mapped_column("NOTE_ID", BigInteger, Sequence("idea_notes_note_id_seq"), primary_key=True)
  user_id: Mapped[int] = mapped_column("USER_ID", BigInteger, ForeignKey("USERS.USER_ID"), nullable=False)
  title: Mapped[str] = mapped_column("TITLE", String(255), nullable=False)
  content: Mapped[dict[str, Any] | list[Any] | None] = mapped_column("CONTENT", JSONB, nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
  updated_at: Mapped[datetime] = mapped_column("UPDATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

  user: Mapped["User"] = relationship("User", back_populates="idea_notes")