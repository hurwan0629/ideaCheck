from datetime import date, datetime

from sqlalchemy import BigInteger, String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

"""
Table USERS {
  USER_ID bigint [pk] // 회원 PK
  USER_NAME varchar // 회원 이름 또는 닉네임
  USER_EMAIL varchar // 대표 이메일
  USER_BIRTH_DATE date // 생년월일
  USER_STATUS varchar // 회원 상태
  USER_CREATED_AT datetime // 생성일시
  USER_UPDATED_AT datetime // 수정일시
}
"""

class User(Base):
  __tablename__ = "USERS"

  user_id: Mapped[int] = mapped_column("USER_ID", BigInteger, primary_key=True)
  user_name: Mapped[str] = mapped_column("USER_NAME", String(100), nullable=False)
  user_email: Mapped[str] = mapped_column("USER_EMAIL", String(255), nullable=False, unique=True)
  user_birth_date: Mapped[date | None] = mapped_column("USER_BIRTH_DATE", Date, nullable=True)
  user_status: Mapped[str] = mapped_column("USER_STATUS", String(100), nullable=False)
  user_created_at: Mapped[datetime] = mapped_column("USER_CREATED_AT", DateTime, nullable=False)
  user_updated_at: Mapped[datetime] = mapped_column("USER_UPDATED_AT", DateTime, nullable=False)