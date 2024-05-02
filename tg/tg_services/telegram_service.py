from uuid import UUID

from aiogram import Bot, Dispatcher
from fastapi import HTTPException

from tg.keyboards.confirm import get_select_confirm_keyboard
from tg.utils.helpers import httpx_request_get


class TelegramService:

    def __init__(self, bot: Bot, dp: Dispatcher):
        self.bot = bot
        self.dp = dp

    async def send_message(self, chat_id: int, text: str, booking_id: int, schedule_id: UUID):
        await self.bot.send_message(
            chat_id,
            text,
            parse_mode='HTML',
            reply_markup=get_select_confirm_keyboard(booking_id=booking_id, schedule_id=schedule_id)
        )

    async def broadcast(self, text: str):

        response = await httpx_request_get(url='/api/v11/user/get_tg_ids')
        if not response.status_code == 200:
            msg = 'Что то не так на сервере'
            raise HTTPException(status_code=500, detail=msg)
        else:
            group = response.json()
            [
                await self.bot.send_message(
                    chat_id,
                    text,
                    parse_mode='HTML',
                ) for chat_id in group
            ]


# Зависимость для инжектирования экземпляра TelegramService
def get_telegram_service() -> TelegramService:
    from tg.bot_init import bot, dp
    return TelegramService(bot, dp)
