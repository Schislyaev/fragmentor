from datetime import datetime, timedelta
from uuid import uuid4

from asyncpg import InternalServerError
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import Column, DateTime, String, select, Boolean, ForeignKey, and_, Integer
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db.postgres import Base, async_session
from db.models.helpers import update_table
from db.models.booking import Booking


class Payment(Base):
    __tablename__ = 'payments'

    id = Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String, default='pending')
    crypto = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    booking = relationship("Booking", back_populates="payment")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(kwargs) > 0:
            self.id = kwargs.get('id')
            self.booking_id = kwargs.get('booking_id')
            self.amount = kwargs.get('amount')
            self.status = kwargs.get('status')
            self.crypto = kwargs.get('crypto', False)

    @classmethod
    async def add(cls, data: dict):
        async with async_session() as session:
            new_record = cls(**data)
            session.add(new_record)
            try:
                await session.commit()
                return new_record.id
            except IntegrityError:
                await session.rollback()
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={'error': 'Payment already exists'})
            except Exception as e:
                await session.rollback()
                # logger.exception(e)
                print(e)
                raise InternalServerError()

    @classmethod
    async def get_by(cls, **f):
        async with async_session() as session:
            result = await session.execute(
                select(cls).options(
                    selectinload(cls.booking).selectinload(Booking.student),
                    selectinload(cls.booking).selectinload(Booking.trainer),
                    selectinload(cls.booking).selectinload(Booking.schedule),
                ).filter_by(**f)
            )
            payment = result.scalars().first()

        # Если платеж найден, получаем связанную информацию
        if payment:
            booking = payment.booking
            return payment, booking
        else:
            return None, None, None, None

    @classmethod
    async def update(cls, payment_id: int, data: dict):
        await update_table(cls, payment_id, data)

        # Подгружаю связь
        async with async_session() as session:
            result = await session.execute(
                select(cls).options(
                    selectinload(cls.booking),
                ).filter_by(id=payment_id)
            )
            payment = result.scalars().first()

        return payment
