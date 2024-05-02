from functools import lru_cache
from uuid import uuid4

from yookassa import Configuration, Payment

from core.settings import settings
from notifications.email_notification import get_email_service
from payments.payment_base import BasePaymentService
from services.booking import get_booking
from services.payment import get_payment
from services.schedule import get_schedule

booking = get_booking()
schedule = get_schedule()
email = get_email_service()
payment = get_payment()


class YookassaService(BasePaymentService):
    def __init__(self):
        self.shop_id = settings.yookassa_shop_id.get_secret_value()
        self.secret_key = settings.yookassa_secret_key.get_secret_value()
        Configuration.configure(self.shop_id, self.secret_key)

    @staticmethod
    def create_payment(amount, return_url=None, description="Оплата заказа", metadata: dict = None):
        idempotency_key = uuid4()
        new_payment = Payment.create({
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description,
            "metadata": idempotency_key
        }, idempotency_key=idempotency_key
        )
        # return new_payment
        return {
            'payment_link': new_payment.confirmation.confirmation_url,
            'payment_id': new_payment.id
        }


@lru_cache()
def get_yookassa() -> YookassaService:
    return YookassaService()
