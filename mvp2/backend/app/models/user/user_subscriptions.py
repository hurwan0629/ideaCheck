from enum import Enum
from datetime import datetime, timezone

from sqlalchemy import Enum as SqlEnum, BigInteger, DateTime, ForeignKey, String, Sequence, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

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
  price_at_purchase: Mapped[float] = mapped_column("PRICE_AT_PURCHASE", Numeric(10, 2), nullable=False)
  started_at: Mapped[datetime] = mapped_column("STARTED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
  ended_at: Mapped[datetime | None] = mapped_column("ENDED_AT", DateTime(timezone=True), nullable=True)
  canceled_at: Mapped[datetime | None] = mapped_column("CANCELED_AT", DateTime(timezone=True), nullable=True)

  user: Mapped["User"] = relationship("User", back_populates="user_subscriptions")
  plan: Mapped["Plan"] = relationship("Plan", back_populates="user_subscriptions")