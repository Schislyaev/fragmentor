import asyncio
from datetime import datetime

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import Column, DateTime, Integer, String, event, select

from db.postgres import Base, async_session


class PaymentSum(Base):
    __tablename__ = 'payment_sums'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @classmethod
    async def get(cls):
        async with async_session() as session:
            try:
                # Построение запроса для выборки пользователя по email
                stmt = select(cls).filter(cls.id == 1)

                # Выполнение запроса и получение результата
                result = await session.execute(stmt)
                return result.scalars().first()  # Получить первую запись

            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": e})


class TGBroadcast(Base):
    __tablename__ = 'tg_broadcasts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


@event.listens_for(TGBroadcast, 'after_insert')
def after_insert(mapper, connection, target):
    from tg.tg_services.telegram_service import get_telegram_service
    telegram = get_telegram_service()

    asyncio.create_task(telegram.broadcast(target.message))
