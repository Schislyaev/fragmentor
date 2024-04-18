import uuid
from functools import lru_cache
from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException, status
from zoneinfo import ZoneInfo

from db.models.schedule import Schedule


class ScheduleService:

    @staticmethod
    async def add_time(time_start: datetime, time_zone: dict, trainer_id: UUID):
        # components = [int(x) for x in time_start.split(", ")]
        #
        # if components[4] % 15 != 0:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail={'message': 'Minutes must be a multiple of 15'}
        #     )
        #
        # datetime_object = datetime(*components[:5], tzinfo=timezone.utc)

        trainer_time_zone = ZoneInfo(time_zone.get('time_zone').key)

        datetime_object = time_start.replace(tzinfo=trainer_time_zone)
        datetime_object_to_save = datetime_object.astimezone((ZoneInfo('UTC')))

        await Schedule.add(time_start=datetime_object_to_save, time_zone=trainer_time_zone, trainer_id=trainer_id)

    @staticmethod
    async def delete_time(record_id: str):
        record_id = UUID(record_id)
        await Schedule.delete(record_id)

    @staticmethod
    async def update(schedule_id, **data):
        schedule = await Schedule.update(schedule_id=schedule_id, data=data)
        return schedule

    @staticmethod
    async def get_timeslots_by_trainer_id(trainer_id: str, student_time_zone):
        trainer_id = UUID(trainer_id)
        schedules = await Schedule.get_by_trainer_id(trainer_id)
        # Учитываем таймзону для отражения местного времени студенту
        times_of_schedule = [schedule.time_start.astimezone(ZoneInfo(student_time_zone.key)) for schedule in schedules]

        return times_of_schedule

    @staticmethod
    async def get_trainers_by_timeslot(timeslot, student_time_zone):
        timeslot_unpacked = timeslot.split('-')
        timeslot_ready = [timeslot_element.split(':') for timeslot_element in timeslot_unpacked]
        timeslot = datetime(
            *[int(element) for elements in timeslot_ready for element in elements],
            tzinfo=ZoneInfo(student_time_zone.key)
        ).astimezone(ZoneInfo('UTC'))

        schedules = await Schedule.get_by_timeslot(timeslot)

        trainers = [schedule.trainer_id for schedule in schedules]

        return trainers


@lru_cache()
def get_schedule() -> ScheduleService:
    return ScheduleService()
