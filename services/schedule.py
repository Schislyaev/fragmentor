from datetime import datetime
from functools import lru_cache
from uuid import UUID
from zoneinfo import ZoneInfo
from collections import defaultdict

from db.models.schedule import Schedule


class ScheduleService:

    @staticmethod
    async def add_time(time_start: datetime, time_zone: dict, trainer_id: UUID):

        trainer_time_zone = ZoneInfo(time_zone.get('time_zone').key)

        datetime_object_to_save = time_start.astimezone((ZoneInfo('UTC')))

        await Schedule.add(time_start=datetime_object_to_save, time_zone=trainer_time_zone, trainer_id=trainer_id)

    @staticmethod
    async def delete_time(record_id: str):
        record_id = UUID(record_id)
        await Schedule.update(schedule_id=record_id, data={'is_deleted': True})
        # await Schedule.delete(record_id)

    @staticmethod
    async def update(schedule_id, **data):
        schedule = await Schedule.update(schedule_id=schedule_id, data=data)
        return schedule

    @staticmethod
    async def get_timeslots_by_trainer_id(trainer_id, student_time_zone):
        # trainer_id = UUID(trainer_id)
        schedules = await Schedule.get_by_trainer_id(trainer_id)
        # Учитываем таймзону для отражения местного времени студенту
        times_of_schedule = [
            {
                'id': schedule.id,
                'time': schedule.time_start.astimezone(ZoneInfo(student_time_zone.key))
            } for schedule in schedules]

        return times_of_schedule

    @staticmethod
    async def get_trainers_by_timeslot(time_start, time_finish, time_zone):

        time_start = datetime(
            year=time_start.year,
            month=time_start.month,
            day=time_start.day,
            hour=time_start.hour,
            minute=time_start.minute,
            tzinfo=ZoneInfo(time_zone.key)
        ).astimezone(ZoneInfo('UTC'))
        time_finish = datetime(
            year=time_finish.year,
            month=time_finish.month,
            day=time_finish.day,
            hour=time_finish.hour,
            minute=time_finish.minute,
            tzinfo=ZoneInfo(time_zone.key)
        ).astimezone(ZoneInfo('UTC'))

        schedules = await Schedule.get_by_timeslot(time_start=time_start, time_finish=time_finish)

        trainers = [
            {
                'trainer_id': str(schedule.trainer_id),
                'schedule_id': str(schedule.id),
                'time_start': schedule.time_start.astimezone(ZoneInfo(time_zone.key)),
            } for schedule in schedules
        ]

        return trainers

    @staticmethod
    async def get_trainers_with_timeslots(time_start, time_finish, time_zone):

        schedules = await Schedule.get_by_timeslot(time_start=time_start, time_finish=time_finish)

        dict_trainers = defaultdict(list)
        [
            dict_trainers[schedule.trainer_id].append(
                {
                    'schedule_id': str(schedule.id),
                    'time_start': schedule.time_start.astimezone(ZoneInfo(time_zone.get('time_zone'))),
                }
            ) for schedule in schedules
        ]

        return dict_trainers


@lru_cache()
def get_schedule() -> ScheduleService:
    return ScheduleService()
