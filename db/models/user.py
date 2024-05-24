from datetime import datetime
from uuid import uuid4

from asyncpg import InternalServerError
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import (Boolean, Column, DateTime, Float, Integer, LargeBinary,
                        String, select)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, selectinload

from db.models.booking import Booking
from db.models.helpers import get_item, update_table
from db.postgres import Base, async_session
from services.helpers import get_password_hash, verify_password


class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    email = Column(String(60), nullable=False, unique=True)
    password = Column(String(60), nullable=True)
    nickname = Column(String(15), nullable=True, unique=True)
    is_trainer = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    is_email_confirmed = Column(Boolean, default=False)
    tg_id = Column(Integer, default=None, unique=True)
    photo = Column(LargeBinary, nullable=True)
    rating_score = Column(Float, nullable=True)  # Колонка для хранения рейтинга
    rating_count = Column(Integer, nullable=True)  # Колонка для хранения количества оценок

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    schedules = relationship('Schedule', back_populates='trainer', cascade="all, delete-orphan")
    bookings_as_student = relationship(
        'Booking', back_populates='student', foreign_keys='Booking.student_id', cascade="all, delete-orphan"
    )
    bookings_as_trainer = relationship(
        'Booking', back_populates='trainer', foreign_keys='Booking.trainer_id', cascade="all, delete-orphan"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(kwargs) > 0:
            self.email = kwargs.get('email')
            self.password = get_password_hash(kwargs.get('password'))
            self.is_trainer = kwargs.get('is_trainer')

    @classmethod
    async def authenticate(cls, email, password):
        user = await cls.get_by_email(email=email)
        if not verify_password(password, user.password):
            return False
        return True

    @classmethod
    async def add(cls, data: dict):
        async with async_session() as session:
            session.add(cls(**data))
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"error": "User already exists"})
            except Exception as e:
                await session.rollback()
                # logger.exception(e)
                print(e)
                raise InternalServerError()

    @classmethod
    async def update(cls, user_id: UUID, data: dict):
        await update_table(cls, user_id, data=data)

    @classmethod
    async def get_by_email(cls, email: str):

        return await get_item(cls, cls.email, email)

    @classmethod
    async def get_by_id(cls, trainer_id: UUID) -> dict:

        return await get_item(cls, cls.user_id, trainer_id)

    @classmethod
    async def fetch_all_tg_ids(cls):
        async with async_session() as session:
            try:
                query = select(cls.tg_id).where(cls.tg_id.isnot(None))  # Фильтруем, чтобы исключить None значения
                result = await session.execute(query)
                tg_ids = result.scalars().all()
                return tg_ids
            except IntegrityError:
                await session.rollback()
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"error": "User already exists"})
            except Exception as e:
                await session.rollback()
                # logger.exception(e)
                print(e)
                raise InternalServerError()

    @classmethod
    async def fetch_all_bookings(cls, user_id, conditions=None):
        try:
            async with async_session() as session:
                # Асинхронно выполняем запрос к базе данных
                query = select(Booking).options(
                    selectinload(Booking.student),
                    selectinload(Booking.trainer),
                    selectinload(Booking.schedule)
                ).where(
                    Booking.trainer_id == user_id,
                    Booking.is_confirmed == True  # noqa
                )

                # Добавление дополнительных условий фильтрации перед выполнением запроса
                if conditions:
                    for key, value in conditions.items():
                        query = query.where(getattr(Booking, key) == value)

                result = await session.execute(query)
                bookings = result.scalars().all()
                return bookings
        except Exception as e:
            await session.rollback()
            # logger.exception(e)
            print(e)
            raise InternalServerError()
