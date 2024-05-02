from http import HTTPStatus

import httpx
from aiogram import types
from bot_init import bot

from core.settings import settings


async def start(message: types.Message):
    """
    Записать пользователя в БД.
    """

    user_id = message.from_user.id

    async with httpx.AsyncClient(timeout=httpx.Timeout(45.0, read=30.0)) as client:
        res = await client.post(
            url=f'http://{settings.url}:{settings.port}/api/v11/user/confirm_tg',
            json=dict(message.from_user)
        )

    messages = {
        'created': 'Привет! Теперь ты связан с нами.',
        'conflict': 'Ты уже с нами',
        'default': 'Со мной что-то не так...'
    }

    match res.status_code:

        case HTTPStatus.CREATED:
            await bot.send_message(
                chat_id=user_id,
                text=messages['created'],
            )
        case HTTPStatus.CONFLICT:
            await bot.send_message(
                chat_id=user_id,
                text=messages['conflict'],
            )
        case _:
            await bot.send_message(
                chat_id=user_id,
                text=messages['default'],
            )
