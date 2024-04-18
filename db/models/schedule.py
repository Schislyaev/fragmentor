from datetime import datetime, timedelta
from uuid import uuid4

from asyncpg import InternalServerError
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import Column, DateTime, String, select, Boolean, ForeignKey, and_
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

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
    booking = relationship("Booking", back_populates="schedule", uselist=False)

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
    async def update(cls, schedule_id: int, data: dict):
        schedule = await update_table(cls, schedule_id, data)
        # async with async_session() as session:
        #     async with session.begin():
        #         try:
        #             # Найти объект по ID
        #             obj = await session.get(cls, schedule_id)
        #             if not obj:
        #                 raise HTTPException(status_code=404, detail="Object not found")
        #
        #             # Обновление атрибутов объекта новыми значениями из data
        #             for key, value in data.items():
        #                 setattr(obj, key, value)
        #
        #             # session.add(obj) # В данном контексте не обязательно, так как изменения отслеживаются
        #             await session.commit()
        #             return obj  # Возвращаем обновленный объект
        #
        #         except SQLAlchemyError as e:
        #             await session.rollback()
        #             # logger.exception(e)
        #             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

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
                            cls.is_deleted is False,
                            cls.is_reserved is False

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
    async def get_by_timeslot(cls, timeslot: datetime):
        async with async_session() as session:
            try:
                # schedules = await session.execute(select(cls).filter_by(time_start=timeslot))
                #
                # :todo Код ниже для реализации более гибкого поиска
                #
                # timeslot_start = timeslot - timedelta(minutes=15)
                # timeslot_end = timeslot + timedelta(minutes=15)
                #
                # # Формирование запроса
                schedules = await session.execute(
                    select(cls)
                    .filter(
                        and_(
                            cls.time_start == timeslot,
                            cls.is_deleted is False,
                            cls.is_reserved is False
                            # cls.time_start >= timeslot_start,
                            # cls.time_start <= timeslot_end,
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
