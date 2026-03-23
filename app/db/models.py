import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TenderResult(str, enum.Enum):
    WON = "WON"
    LOST = "LOST"
    MISSED = "MISSED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    tenders: Mapped[list["TenderEvent"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class TenderEvent(Base):
    __tablename__ = "tender_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    tender_number: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    customer_name: Mapped[str] = mapped_column(String(255))
    region: Mapped[str] = mapped_column(String(255), index=True)
    okpd2: Mapped[str] = mapped_column(String(16), index=True)
    nmck: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    final_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    result: Mapped[TenderResult] = mapped_column(Enum(TenderResult, name="tender_result"))
    reduction_pct: Mapped[float] = mapped_column(default=0.0)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    user: Mapped[User] = relationship(back_populates="tenders")
