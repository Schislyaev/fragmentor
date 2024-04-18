from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from core.logger import log

logger = log(__name__)


class IgnoreBotsMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if not data.get('event_from_user').is_bot:
            return await handler(event, data)
        logger.warning(f'{data.get("event_from_user").id} Bot message')
        return
