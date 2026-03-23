from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select

from app.db.base import Base
from app.db.models import TenderEvent, TenderResult, User
from app.db.session import SessionLocal, engine


def seed() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.email == "demo@etp-pro.ru"))
        if existing is None:
            existing = User(id="11111111-1111-1111-1111-111111111111", email="demo@etp-pro.ru")
            db.add(existing)
            db.flush()

        db.query(TenderEvent).filter(TenderEvent.user_id == existing.id).delete()

        rows = [
            TenderEvent(
                id=str(uuid4()),
                user_id=existing.id,
                tender_number="ETP-2026-0001",
                title="Поставка лабораторного оборудования",
                customer_name="ГБУЗ НИИ Технологий",
                region="Москва",
                okpd2="26.51",
                nmck=Decimal("4500000.00"),
                final_price=Decimal("4120000.00"),
                result=TenderResult.WON,
                reduction_pct=8.4,
                published_at=datetime.fromisoformat("2026-01-15T00:00:00+00:00"),
            ),
            TenderEvent(
                id=str(uuid4()),
                user_id=existing.id,
                tender_number="ETP-2026-0002",
                title="Поставка серверного оборудования",
                customer_name="АО Центр Данных",
                region="Санкт-Петербург",
                okpd2="26.20",
                nmck=Decimal("11200000.00"),
                final_price=Decimal("10900000.00"),
                result=TenderResult.LOST,
                reduction_pct=2.7,
                published_at=datetime.fromisoformat("2025-12-22T00:00:00+00:00"),
            ),
        ]

        db.add_all(rows)
        db.commit()


if __name__ == "__main__":
    seed()
