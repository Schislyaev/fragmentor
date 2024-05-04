from functools import lru_cache
from uuid import UUID
from zoneinfo import ZoneInfo

from db.models.booking import Booking
from db.models.schedule import Schedule
from db.models.user import User
from notifications.email_notification import get_email_service
from services.schedule import get_schedule

schedule = get_schedule()
email = get_email_service()


class BookingService:

    @staticmethod
    async def create(
            schedule_id: str,
            time_zone_student: str,
            email: str
    ):
        """ Принимаем из фронта uuid записи расписания, из токена таймзону студента и студента"""

        schedule_id = schedule_id
        schedule_data = await Schedule.get_by_id(UUID(schedule_id))
        trainer_id = schedule_data.trainer_id
        time_zone_trainer = schedule_data.time_zone
        time_start = schedule_data.time_start

        student = await User.get_by_email(email)
        trainer = await User.get_by_id(trainer_id)

        tg_id = trainer.tg_id

        data_to_create = {
            'time_start': time_start,
            'trainer_id': trainer_id,
            'time_zone_trainer': time_zone_trainer,
            'student_id': student.user_id,
            'time_zone_student': time_zone_student,
            'schedule_id': schedule_id,
        }

        booking_id = await Booking.add(data_to_create)

        message = f"""
        Появилась бронь на твое расписание:

        <b>{time_start.astimezone(ZoneInfo(time_zone_trainer)).strftime('%Y-%m-%d %H:%M')}</b>

        Подтверждаешь?\n
        """
        # {
        #     tg_id: tg_id,
        #     time_start: time_start,
        #     time_zone_trainer: time_zone_trainer
        # }

        return tg_id, message, booking_id

    @staticmethod
    async def update_and_get_emails(booking_id: int, **data):
        booking, student_email, trainer_email = await Booking.update(booking_id=booking_id, data=data)

        return student_email, trainer_email

    async def cancel(self, booking_id: int, schedule_id: UUID):
        # Пометить время тренера из его календаря, как удаленное.
        await schedule.update(str(schedule_id), is_deleted=True)

        # Пометить бронь как удаленную
        student_email, trainer_email = await self.update_and_get_emails(booking_id=booking_id, is_deleted=True)

        # Оповестить студента об отказе тренера на это время.
        await email.send(
            message_id=booking_id,
            subject='Отмена брони',
            message='Ваша бронь отменена, тренер нас подвел и отказался учить в это время',
            destinations=['pschhhh@gmail.com', student_email]
        )

    @staticmethod
    async def get_emails(booking_id: int):
        return await Booking.get_emails_by_id(booking_id=booking_id)


@lru_cache()
def get_booking() -> BookingService:
    return BookingService()
