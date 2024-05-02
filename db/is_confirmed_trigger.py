import asyncio
import json

import asyncpg

from core.settings import settings


async def listen_notifications():
    conn = await asyncpg.connect(dsn=settings.database_url_trigger)
    await conn.add_listener('field_change', notification_handler)
    await asyncio.Future()  # Задерживаем завершение функции


async def notification_handler(connection, pid, channel, payload):
    record = json.loads(payload)
    if record.get('is_confirmed'):
        ...  # тут должна быть логика создания канала
    print(f"Получено уведомление: {payload}")


if __name__ == '__main__':
    asyncio.run(listen_notifications())
