from datetime import datetime
from uuid import uuid4

from asyncpg import InternalServerError
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import Column, DateTime, String, select, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db.postgres import Base, async_session
from services.helpers import get_password_hash, verify_password
from db.models.schedule import Schedule
from db.models.booking import Booking
from db.models.helpers import update_table, get_item


class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    email = Column(String(60), nullable=False, unique=True)
    password = Column(String(60), nullable=True)
    is_trainer = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    tg_id = Column(Integer, default=None, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    schedules = relationship('Schedule', back_populates='trainer')
    bookings_as_student = relationship('Booking', back_populates='student', foreign_keys='Booking.student_id')
    bookings_as_trainer = relationship('Booking', back_populates='trainer', foreign_keys='Booking.trainer_id')

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
    async def get_by_email(cls, email: str) -> dict:

        return await get_item(cls, cls.email, email)

    @classmethod
    async def get_by_id(cls, trainer_id: UUID) -> dict:

        return await get_item(cls, cls.user_id, trainer_id)

    @classmethod
    async def fetch_all_tg_ids(cls):
        # async with session.begin():
        #     query = select(User.tg_id).where(User.tg_id.isnot(None))  # Фильтруем, чтобы исключить None значения
        #     result = await session.execute(query)
        #     tg_ids = result.scalars().all()
        #     return tg_ids
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
