# from cashews import cache
import uuid
from uuid import UUID

from fastapi import APIRouter, Body, Depends, status, HTTPException, Response, Path
from fastapi.responses import JSONResponse
from jose import JWTError, jwt

from services.security import oauth2_scheme, check_user, get_payload
from server.api.schemas.schedule import TimeSlotIn
from services.booking import BookingService, get_booking
from tg.tg_services.telegram_service import get_telegram_service, TelegramService
from tg.bot_init import bot, dp

# telegram = TelegramService(bot, dp)

router = APIRouter()


@router.post(
    path='/booking/create',
    summary='Зарезервировать время',
    description='Выбрать время',
    response_description='Подтверждение выбора, ожидание подтверждения тренера',
    response_model=None
    # dependencies=[Depends(oauth2_scheme)]
)
# @cache(
#     ttl=settings.redis_cash_timeout,
#     key='{film_id}'
# )
async def reservation_create(
        token: str = Depends(oauth2_scheme),
        booking: BookingService = Depends(),
        telegram: TelegramService = Depends(get_telegram_service),
        schedule_id: str = Body(...)
) -> JSONResponse:
    # Сохранить бронь (время, тренер) V
    # Послать оповещение тренеру V
    # > Дождаться подтверждения тренера
    # Оплата
    # Создание ссылки на дискорд

    payload = get_payload(token)

    booking_data = {
        'email': payload.get('sub'),
        'time_zone_student': payload.get('time_zone'),
        'schedule_id': schedule_id
    }

    trainer_tg_id, message, booking_id = await booking.create(**booking_data)

    await telegram.send_message(
        trainer_tg_id,
        message,
        booking_id=booking_id,
        schedule_id=schedule_id
    )

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={'message': 'Booking added'})


@router.post(
    path='/booking/cancel',
    summary='Отменить время',
    description='Отменить время',
    response_description='Отмена резерва',
    response_model=None
    # dependencies=[Depends(oauth2_scheme)]
)
# @cache(
#     ttl=settings.redis_cash_timeout,
#     key='{film_id}'
# )
async def booking_cancel(
        booking: BookingService = Depends(get_booking),
        data: dict = Body(...)
):
    booking_id = data.get('booking_id')
    schedule_id = UUID(data.get('schedule_id'))

    await booking.cancel(booking_id, schedule_id)
