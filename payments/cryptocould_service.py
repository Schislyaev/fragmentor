from core.settings import settings
from payments.cryptocloud_base import CryptoCloudSDK
from payments.payment_base import BasePaymentService

base_cryptocloud = CryptoCloudSDK(api_key=settings.cryptocloud_api_key.get_secret_value())


class CryptoCouldService(BasePaymentService):

    @staticmethod
    def create_payment(amount, return_url=None, description="Оплата заказа", metadata: dict = None):
        invoice_data = {
            'amount': amount,
            'currency': 'RUB',
            'shop_id': settings.cryptocloud_shop_id.get_secret_value(),
        }

        response = base_cryptocloud.create_invoice(invoice_data=invoice_data)
        payment_link = response.get('result').get('link')
        payment_id = response.get('result').get('uuid').split('-')[1]

        return {
            'payment_link': payment_link,
            'payment_id': payment_id
        }


def get_cryptocloud() -> CryptoCouldService:
    return CryptoCouldService()
