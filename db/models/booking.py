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


class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, autoincrement=True)

    trainer_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey('schedules.id'), nullable=False)

    time_start = Column(DateTime(timezone=True), nullable=False)
    time_zone_trainer = Column(String(), default='UTC')
    time_zone_student = Column(String(), default='UTC')
    is_confirmed = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    student = relationship('User', back_populates='bookings_as_student', foreign_keys=[student_id])
    trainer = relationship('User', back_populates='bookings_as_trainer', foreign_keys=[trainer_id])
    payment = relationship("Payment", back_populates="booking")
    schedule = relationship("Schedule", back_populates="booking", uselist=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(kwargs) > 0:
            self.trainer_id = kwargs.get('trainer_id')
            self.student_id = kwargs.get('student_id')
            self.schedule_id = kwargs.get('schedule_id')
            self.time_start = kwargs.get('time_start')
            self.time_zone_trainer = kwargs.get('time_zone_trainer')
            self.time_zone_student = kwargs.get('time_zone_student')

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
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"error": "Booking already exists"})
            except Exception as e:
                await session.rollback()
                # logger.exception(e)
                print(e)
                raise InternalServerError()

    @classmethod
    async def get_by_id(cls, booking_id: UUID):
        async with async_session() as session:
            try:
                # Построение запроса для выборки пользователя по id
                stmt = select(Booking).filter(Booking.id == booking_id)

                # Выполнение запроса и получение результата
                result = await session.execute(stmt)
                booking = result.scalars().first()  # Получить первую запись

                return booking
            except Exception:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "Booking not found"})

    @classmethod
    async def update(cls, booking_id: int, data: dict):
        await update_table(cls, booking_id, data)

        # Подгружаю связь
        async with async_session() as session:
            result = await session.execute(
                select(Booking).options(
                    selectinload(Booking.student),
                    selectinload(Booking.trainer)
                ).filter_by(id=booking_id)
            )
            booking = result.scalars().first()
            student_email = booking.student.email
            trainer_email = booking.trainer.email

        return booking, student_email, trainer_email

    @classmethod
    async def get_emails_by_id(cls, booking_id: int):

        # Подгружаю связь
        # async with async_session() as session:
        #     result = await session.execute(
        #         select(Booking).options(
        #             selectinload(Booking.student),
        #             selectinload(Booking.trainer)
        #         ).filter_by(id=booking_id)
        #     )
        #     booking = result.scalars().first()
        booking = await load_relationships(cls, booking_id)
        student_email = booking.student.email
        trainer_email = booking.trainer.email

        return student_email, trainer_email


async def load_relationships(cls, booking_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(cls).options(
                selectinload(cls.student),
                selectinload(cls.trainer)
            ).filter_by(id=booking_id)
        )
    return result.scalars().first()
