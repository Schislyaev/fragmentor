from db.models.payment import Payment
from functools import lru_cache


class PaymentService:

    @staticmethod
    async def create(payment_id, booking_id, amount, crypto=False):
        payment_data = {
            'id': payment_id,
            'booking_id': booking_id,
            'amount': amount,
            'crypto': crypto
        }
        await Payment.add(data=payment_data)

    @staticmethod
    async def update(payment_id, **data):
        await Payment.update(payment_id=payment_id, data=data)

    @staticmethod
    async def get_booking_by_payment_id(payment_id):
        return await Payment.get_by(id=payment_id)


@lru_cache()
def get_payment() -> PaymentService:
    return PaymentService()
