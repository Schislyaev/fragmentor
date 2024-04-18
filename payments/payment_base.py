from core.settings import settings
from uuid import UUID
from services.booking import get_booking
from services.schedule import get_schedule
from notifications.email_notification import get_email_service
from services.payment import get_payment
from AdminPanel.admin_helper_models import PaymentSum
import httpx
from services import helpers

booking = get_booking()
schedule = get_schedule()
email = get_email_service()
payment = get_payment()


class BasePaymentService:

    @staticmethod
    def create_payment(amount, return_url=None, description="Оплата заказа", metadata: dict = None):
        return ...

    def collect_and_create_payments(self, amount, description="Оплата заказа",) -> list[dict]:
        payments_info = [
            subclass().create_payment(
                amount,
                description
            ) for subclass in self.__class__.__subclasses__()
        ]

        return payments_info

    async def process(self, booking_id):

        # Перевести бронь в статус confirmed.
        student_email, _ = await booking.update_and_get_emails(
            booking_id=booking_id,
            is_confirmed=True
        )

        # Создать платеж и получить ссылку.
        # Собираю все платежные системы перебиранием подклассов
        payment_sum = (await PaymentSum.get()).amount
        payments_info = self.collect_and_create_payments(
            amount=payment_sum,
        )

        # Записать данные платежей в базу.
        # Связать платежи и бронь,
        # Списковым включением фильтрую крипту и некрипту.
        [
            await payment.create(
                payment_id=helpers.encode_id_to_uuid_style(payment_info['payment_id']) if len(
                    payment_info['payment_id']) != 36 else payment_info['payment_id'],
                booking_id=booking_id,
                amount=payment_sum,
                crypto=True if len(payment_info['payment_id']) != 36 else False
            ) for payment_info in payments_info
        ]

        # Оповестить студента и выдать ему ссылку на оплату.
        await email.send(
            message_id=booking_id,
            subject='Бронь подтверждена',
            message=f'Ваши ссылки на оплату:\nСтандартно: {payments_info[0]["payment_link"]}\n'
                    f'Crypto: {payments_info[1]["payment_link"]}',
            destinations=['pschhhh@gmail.com', 'schislyaev@gmail.com'],  # student_email
        )

    @staticmethod
    async def on_payed(payment_id: UUID | str):

        payment_obj, booking_obj = await payment.get_booking_by_payment_id(payment_id=payment_id)
        booking_id = booking_obj.id
        schedule_id = booking_obj.schedule.id

        # записываем платеж как оплаченный
        await payment.update(
            payment_id=payment_id,
            status='succeeded'
        )

        # записываем время тренера как забронированное
        await schedule.update(
            schedule_id=schedule_id,
            is_reserved=True
        )

        # отправить запрос на дискорд бот и получить ссылки-приглашения
        async with httpx.AsyncClient(timeout=httpx.Timeout(45.0, read=30.0)) as client:
            try:
                response = await client.post(
                    url=f'http://{settings.discord_host}:8888/discord/create_channel',
                    json={'guild_id': settings.discord_guild_id, 'channel_name': f'chanel_{str(booking_id)}'}
                )
                invites = response.json()
                invite1 = invites.get('link1')
                invite2 = invites.get('link2')
            except Exception as e:
                raise e

        # отправляем оповещение пользователю, что платеж прошел успешно и прикладываем ссылку на дискорд
        student_email, trainer_email = await booking.get_emails(booking_id=booking_id)
        await email.send(
            message_id=booking_id,
            subject='Ссылка на занятие',
            message=f'Оплата прошла успешно!\n\nТвоя ссылка на занятие:\n{invite1}',
            destinations=[student_email]
        )
        # отправляем ссылку на дискорд тренеру
        await email.send(
            message_id=booking_id,
            subject='Ссылка на занятие',
            message=f'Твоя ссылка на занятие:\n{invite2}',
            destinations=[trainer_email]
        )

    @staticmethod
    async def on_canceled(payment_id: UUID | str):

        await payment.update(
            payment_id=payment_id,
            status='canceled'
        )


def get_base_payment() -> BasePaymentService:
    return BasePaymentService()
