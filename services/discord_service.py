import httpx
from functools import lru_cache
from fastapi.responses import JSONResponse
from core.settings import settings


class DiscordService:
    def __init__(self):
        self.discord_web_service_url = settings.discord_web_service_url
        self.guild_id = settings.discord_guild_id

    async def get_channels(self, channel_name: str) -> JSONResponse | Exception:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.discord_web_service_url,
                    json={"guild_id": self.guild_id, "channel_name": channel_name}
                )
                return JSONResponse(status_code=response.status_code, content=response.json())
            except Exception as e:
                raise e


@lru_cache()
def get_discord_service() -> DiscordService:
    return DiscordService()
