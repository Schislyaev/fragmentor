# from cashews import cache
from urllib.parse import parse_qs

from fastapi import APIRouter, Body, Depends, Request, Response, status
from fastapi.responses import JSONResponse

from core.settings import settings
from db.redis import Redis, get_redis
from payments.cryptocould_service import CryptoCouldService, get_cryptocloud
from payments.payment_base import BasePaymentService, get_base_payment
from payments.yookassa_service import YookassaService, get_yookassa
from services import helpers

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

router = APIRouter()


@router.get(
    path='/return_from_payment',
    summary='Обратная ссылка платежа',
    description='Получить информацию о платеже',
    response_description='',
)
# @cache(
#     ttl=settings.redis_cash_timeout,
#     key='{film_id}'
# )
async def return_from_payment(
        request: Request,
):
    ...
    return JSONResponse(status_code=status.HTTP_200_OK, content={'message': 'OK'})


@router.post(
    path='/payment/get_payment_status_yookassa',
    summary='Инфо платежа',
    description='Произошла ли оплата',
    response_description='',
)
# @cache(
#     ttl=settings.redis_cash_timeout,
#     key='{film_id}'
# )
async def get_payment_status_yookassa(
        data: dict = Body,
        service: YookassaService = Depends(get_yookassa),
        redis: Redis = Depends(get_redis)
):
    payment_id = data.get('object').get('id')

    # Юкасса повторяет коллбеки (пока не понимаю почему).
    # Для устранения не нужных процессов делаю проверку в редис
    if await redis.exists(payment_id):
        return Response(status_code=status.HTTP_200_OK)
    else:
        await redis.set(payment_id, str(payment_id), ex=300)

    payment_status = data.get('event')
    if payment_status == 'payment.succeeded':
        await service.on_payed(payment_id=payment_id)

    elif payment_status == 'payment.canceled':
        await service.on_canceled(payment_id=payment_id)

    return Response(status_code=status.HTTP_200_OK)


@router.post(
    path='/payment/get_payment_status_cryptocloud',
    summary='Инфо платежа',
    description='Произошла ли оплата',
    response_description='',
)
# @cache(
#     ttl=settings.redis_cash_timeout,
#     key='{film_id}'
# )
async def get_payment_status_cryptocloud(
        data: bytes = Body(...),
        service: CryptoCouldService = Depends(get_cryptocloud),
        redis: Redis = Depends(get_redis)
):
    query_string = data.decode('utf-8')
    parsed_data = parse_qs(query_string)
    payment_status = parsed_data.get('status')[0]
    payment_id = parsed_data.get('invoice_id')[0]
    payment_id = helpers.encode_id_to_uuid_style(payment_id)

    # Для устранения не нужных процессов делаю проверку в редис
    if await redis.exists(str(payment_id)):
        return Response(status_code=status.HTTP_200_OK)
    else:
        await redis.set(str(payment_id), str(payment_id), ex=300)

    if payment_status == 'success':
        await service.on_payed(payment_id=payment_id)

    else:
        await service.on_canceled(payment_id=payment_id)

    return Response(status_code=status.HTTP_200_OK)


@router.post(
    path='/payment/create_payment',
    summary='Создание платежа',
    description='Создание платежа',
    response_description='',
)
# @cache(
#     ttl=settings.redis_cash_timeout,
#     key='{film_id}'
# )
async def create_payment(
        # payment: YookassaService = Depends(get_yookassa),
        payment: BasePaymentService = Depends(get_base_payment),
        data: dict = Body(...)
):
    booking_id = data.get('booking_id')

    await payment.process(
        booking_id=booking_id,
    )

    return Response(status_code=status.HTTP_200_OK)
