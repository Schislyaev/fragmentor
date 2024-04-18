"""
TG Bot interacting with API for

******  FragMentor  ******

Designed to work through REST API.
In this project I use FastAPI as backend API

Petr Schislyaev
26.03.2024
"""
import asyncio
from time import sleep

from aiogram.filters import Command
from aiogram.exceptions import (TelegramNetworkError, TelegramRetryAfter,
                                TelegramServerError)
from bot_init import bot, dp
from middlewares.bot_handle import IgnoreBotsMiddleware
from utils.commands import set_commands

from core.logger import log
from core.settings import settings
from handlers import register
from utils.statesemail import StepsEmail
from handlers.confirm_booking import select_confirm_confirm_bookings, select_confirm_booking
from callbacks.callbackdata import ConfirmConfirm, Confirm

# logger = log(__name__)


async def on_startup():
    await set_commands()
    print('Up...')
    # logger.info('Started')
    await bot.send_message(
        chat_id=settings.tg_admin_id,
        text='Я проснулся',
    )


async def on_shutdown():
    print('Down...')
    # logger.info('Down')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.message.outer_middleware(IgnoreBotsMiddleware())
    dp.message.register(register.register_user, Command(commands='register'))  # Первый шаг привязки
    dp.message.register(register.get_email, StepsEmail.GET_EMAIL)  # Второй шаг привязки
    dp.callback_query.register(
        select_confirm_booking,
        Confirm.filter()
    )
    dp.callback_query.register(
        select_confirm_confirm_bookings,
        ConfirmConfirm.filter()
    )  # Получили окончательное да/нет, запускаем обработку

    # dp.include_router(add_movie.router)

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(
            bot,
        )
    except (TelegramRetryAfter, TelegramNetworkError, TelegramServerError) as e:
        # logger.exception(e)
        sleep(10)
    except Exception as e:
        ...
    # logger.exception(e)

    finally:
        await bot.send_message(
            chat_id=settings.tg_admin_id,
            text='Я упал',
        )
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
