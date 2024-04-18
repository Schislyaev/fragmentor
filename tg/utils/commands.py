from aiogram.types import BotCommand
from bot_init import bot


async def set_commands():
    commands = [
        BotCommand(
            command='register',
            description='Связать TG с FragMentor"'
        ),
    ]

    await bot.set_my_commands(commands)
