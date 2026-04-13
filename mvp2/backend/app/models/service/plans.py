from enum import Enum
from datetime import datetime, timezone

from sqlalchemy import Enum as SqlEnum, BigInteger, String, Text, Numeric, DateTime, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

"""
Table PLANS {
  PLAN_ID bigint [pk] // 요금제 PK
  PLAN_NAME varchar // 요금제명
  DESCRIPTION text // 요금제 설명
  PRICE decimal // 가격
  BILLING_CYCLE varchar // monthly, yearly 등
  CREATED_AT datetime // 생성일시
}
"""

# 구독 상태
class BillingCycle(str, Enum):
  NONE = "NONE"
  MONTHLY = "MONTHLY"
  YEARLY = "YEARLY"

class PlanName(str, Enum):
  FREE = "FREE"
  PREMIUM = "PREMIUM"

class Plan(Base):
  __tablename__ = "PLANS"

  plan_id: Mapped[int] = mapped_column("PLAN_ID", BigInteger, Sequence("plans_plan_id_seq"), primary_key=True)
  plan_name: Mapped[PlanName] = mapped_column("PLAN_NAME", SqlEnum(PlanName), nullable=False)
  description: Mapped[str | None] = mapped_column("DESCRIPTION", Text, nullable=True)
  price: Mapped[float] = mapped_column("PRICE", Numeric(10, 2), nullable=False)
  billing_cycle: Mapped[BillingCycle] = mapped_column("BILLING_CYCLE", SqlEnum(BillingCycle), nullable=False, default=BillingCycle.NONE)
  created_at: Mapped[datetime] = mapped_column("CREATED_AT", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

  user_subscriptions: Mapped[list["UserSubscription"]] = relationship("UserSubscription", back_populates="plan")