from enum import Enum

from datetime import datetime, timezone
from sqlalchemy import Enum as SqlEnum, BigInteger, String, DateTime, ForeignKey, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

"""
Table AUTH_ACCOUNTS {
  AUTH_ID bigint [pk] // 인증방식 PK
  USER_ID bigint [ref: > USERS.USER_ID] // 회원 FK
  PROVIDER varchar // local, google, kakao, naver
  PROVIDER_USER_ID varchar // 소셜 제공자 고유 ID
  LOGIN_ID varchar // 일반 로그인 아이디
  PASSWORD_HASH varchar // 일반 로그인 비밀번호 해시
  CREATED_AT datetime // 생성일시
}
"""

class AuthProvider(str, Enum):
  LOCAL= "LOCAL"
  GOOGLE= "GOOGLE"
  KAKAO= "KAKAO"

class AuthAccount(Base):
  __tablename__ = "AUTH_ACCOUNTS"

  auth_id: Mapped[int] = mapped_column("AUTH_ID", BigInteger, Sequence("auth_accounts_auth_id_seq"), primary_key=True)
  user_id: Mapped[int] = mapped_column("USER_ID", BigInteger, ForeignKey("USERS.USER_ID"), nullable=False)
  provider: Mapped[AuthProvider] = mapped_column("PROVIDER", SqlEnum(AuthProvider), nullable=False)
  provider_user_id: Mapped[str | None] = mapped_column("PROVIDER_USER_ID", String(255), nullable=True)
  login_id: Mapped[str | None] = mapped_column("LOGIN_ID", String(255), nullable=True, unique=True)
  password_hash: Mapped[str | None] = mapped_column("PASSWORD_HASH", String(255), nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  user: Mapped["User"] = relationship("User", back_populates="auth_accounts")