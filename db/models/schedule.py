from datetime import datetime
from uuid import uuid4

from asyncpg import InternalServerError
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import Column, DateTime, String, select, Boolean, ForeignKey, and_
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base, async_session
from db.models.helpers import update_table


class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    trainer_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    time_start = Column(DateTime(timezone=True), nullable=False)
    time_zone = Column(String(), default='UTC')
    is_reserved = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    trainer = relationship('User', back_populates='schedules')
    booking = relationship("Booking", back_populates="schedule", uselist=False,  cascade="all, delete-orphan")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(kwargs) > 0:
            self.time_start = kwargs.get('time_start')
            self.time_zone = str(kwargs.get('time_zone'))
            self.trainer_id = kwargs.get('trainer_id')

    @classmethod
    async def add(cls, **data):
        async with async_session() as session:
            session.add(cls(**data))
            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                # logger.exception(e)
                print(e)
                raise InternalServerError()

    @classmethod
    async def delete(cls, record_id: UUID):
        async with async_session() as session:
            to_delete = await session.execute(select(cls).filter_by(id=record_id))
            to_delete = to_delete.scalars().all()

            if len(to_delete) == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Record {record_id} does not exist')

            await session.delete(to_delete[0])

            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                # logger.exception(e)
                print(e)
                raise InternalServerError()

    @classmethod
    async def update(cls, schedule_id: int | UUID, data: dict):
        schedule = await update_table(cls, schedule_id, data)

        return schedule

    @classmethod
    async def get_by_trainer_id(cls, trainer_id: UUID):
        async with async_session() as session:
            try:
                schedules = await session.execute(
                    select(cls)
                    .filter(
                        and_(
                            cls.trainer_id == trainer_id,
                            # Добавление фильтра, чтобы time_start было позже текущего времени
                            cls.time_start > datetime.now(),
                            cls.is_deleted == False,
                            cls.is_reserved == False

                            # :todo Такая же функция для истории но без условия выше
                        )
                    )
                )
                schedules = schedules.scalars().all()
                return schedules
            except Exception as e:  # :todo Change to right exception
                await session.rollback()
                # logger.exception(e)
                print(e)
                raise InternalServerError()

    @classmethod
    async def get_by_timeslot(cls, time_start: datetime, time_finish: datetime):
        async with async_session() as session:
            try:
                from db.models.user import User
                schedules = await session.execute(
                    select(cls)
                    .join(User, cls.trainer_id == User.user_id)
                    .filter(
                        and_(
                            cls.time_start >= time_start,
                            cls.time_start <= time_finish,
                            cls.is_deleted == False,
                            cls.is_reserved == False,
                            User.tg_id != None  # Не должны показываться слоты тренеров без привязки к ТГ
                        )
                    )
                )

                schedules = schedules.scalars().all()
                return schedules

            except Exception as e:  # :todo Change to right exception
                await session.rollback()
                # logger.exception(e)
                print(e)
                raise InternalServerError()

    @classmethod
    async def get_by_id(cls, schedule_id: UUID):
        async with async_session() as session:
            try:
                stmt = select(Schedule).filter(Schedule.id == schedule_id)

                result = await session.execute(stmt)
                schedule = result.scalars().first()  # Получить первую запись

                if schedule.is_deleted:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "Schedule not found"})

                return schedule
            except Exception:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "Schedule not found"})
