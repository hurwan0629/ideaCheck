from enum import Enum
from datetime import datetime, timezone

from sqlalchemy import Enum as SqlEnum, BigInteger, DateTime, ForeignKey, String, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

"""
Table USER_SUBSCRIPTIONS {
  SUBSCRIPTION_ID bigint [pk] // 회원 구독 PK
  USER_ID bigint [ref: > USERS.USER_ID] // 회원 FK
  PLAN_ID bigint [ref: > PLANS.PLAN_ID] // 요금제 FK
  STATUS varchar // 구독 상태
  STARTED_AT datetime // 구독 시작일시
  ENDED_AT datetime // 구독 종료일시
  CREATED_AT datetime // 생성일시
}
"""

# 구독 상태
class SubscriptionStatus(str, Enum):
  ACTIVE = "ACTIVE"
  CANCELED = "CANCELED"
  EXPIRED = "EXPIRED"
  PAUSED = "PAUSED"

class UserSubscription(Base):
  __tablename__ = "USER_SUBSCRIPTIONS"

  subscription_id: Mapped[int] = mapped_column("SUBSCRIPTION_ID", BigInteger, Sequence("user_subscriptions_subscription_id_seq"), primary_key=True)
  user_id: Mapped[int] = mapped_column("USER_ID", BigInteger, ForeignKey("USERS.USER_ID"), nullable=False)
  plan_id: Mapped[int] = mapped_column("PLAN_ID", BigInteger, ForeignKey("PLANS.PLAN_ID"), nullable=False)
  status: Mapped[SubscriptionStatus] = mapped_column("STATUS", SqlEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
  started_at: Mapped[datetime] = mapped_column("STARTED_AT", DateTime(timezone=True), nullable=False)
  ended_at: Mapped[datetime | None] = mapped_column("ENDED_AT", DateTime(timezone=True), nullable=True)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  user: Mapped["User"] = relationship("User", back_populates="user_subscriptions")
  plan: Mapped["Plan"] = relationship("Plan", back_populates="user_subscriptions")