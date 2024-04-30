# from cashews import cache
from typing import Any
from uuid import UUID
import json

from fastapi import APIRouter, Body, Depends, status, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse
from jose import jwt

from services.security import oauth2_scheme, get_payload, check_user_get_id
from services.booking import BookingService, get_booking
from services.web_socket import WebSocketManager, get_websocket
from tg.tg_services.telegram_service import get_telegram_service, TelegramService


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
        schedule_id: dict = Body(...)
) -> JSONResponse:
    # Сохранить бронь (время, тренер) V
    # Послать оповещение тренеру V.
    # Дождаться подтверждения тренера
    # Оплата
    # Создание ссылки на дискорд

    payload = get_payload(token)
    schedule_id = schedule_id.get('schedule_id')

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


# @router.websocket(
#     path="/ws/{channel_id}"
# )
# async def websocket_endpoint(
#         channel_id: Any,
#         websocket: WebSocket,
#         manager: WebSocketManager = Depends(get_websocket),
#         token: str = Query(...)
# ):
#     try:
#         user_id = await check_user_get_id(token)
#         await manager.connect(websocket)
#
#         while True:
#             data = await websocket.receive_text()
#             data = json.loads(data)
#             message_type = data.get('type')
#
#             if message_type == 'init':
#                 manager.active_connections[user_id] = websocket
#
#             if message_type == 'update_status':
#                 booking_id = data.get('booking_id')
#                 booking_status = data.get('booking_status')
#                 await manager.send_personal_message(
#                     json.dumps({'type': 'update_status', 'booking_id': booking_id, 'booking_status': booking_status}),
#                     user_id
#                 )
#     except jwt.JWTError:
#         await websocket.close(code=1008)
#     except WebSocketDisconnect as e:
#         # await manager.disconnect(user_id)
#         print(f'Connection with {user_id} closed with {e}')
