from enum import Enum
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import Enum as SqlEnum, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.db import Base

"""
Table USER_IDEAS {
  IDEA_ID bigint [pk] // 사용자 원본 아이디어 PK
  USER_ID bigint [ref: > USERS.USER_ID] // 회원 FK
  TITLE varchar // 아이디어 제목
  CONTENT text // 아이디어 원문
  STATUS varchar // 아이디어 상태
  CREATED_AT datetime // 생성일시
  UPDATED_AT datetime // 수정일시
}
"""

class IdeaStatus(str, Enum):
  DRAFT = "DRAFT"
  ACTIVE = "ACTIVE"
  ARCHIVED = "ARCHIVED"

class UserIdea(Base):
  __tablename__ = "USER_IDEAS"

  idea_id: Mapped[int] = mapped_column("IDEA_ID", BigInteger, primary_key=True)
  user_id: Mapped[int] = mapped_column("USER_ID", BigInteger, ForeignKey("USERS.USER_ID"), nullable=False)
  title: Mapped[str] = mapped_column("TITLE", String(255), nullable=False)
  content: Mapped[dict[str, Any]] = mapped_column("CONTENT", JSONB, nullable=False)
  status: Mapped[IdeaStatus] = mapped_column("STATUS", SqlEnum(IdeaStatus), nullable=False, default=IdeaStatus.DRAFT)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
  updated_at: Mapped[datetime] = mapped_column("UPDATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)