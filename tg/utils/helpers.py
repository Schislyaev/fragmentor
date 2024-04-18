from tg.utils.security import create_access_token
import httpx
from core.settings import settings


async def httpx_request_get(url: str):
    access_token = create_access_token(data={})
    async with httpx.AsyncClient(timeout=httpx.Timeout(45000.0, read=30.0)) as client:
        try:
            response = await client.get(
                url=f'http://{settings.host}:{8080}{url}',
                headers={'Authorization': f'Bearer {access_token}'},
            )
        except Exception as e:
            raise e

    return response


async def httpx_request_patch(url: str, **data):
    access_token = create_access_token(data={})
    async with httpx.AsyncClient(timeout=httpx.Timeout(450000.0, read=30.0)) as client:
        try:
            response = await client.patch(
                url=f'http://{settings.host}:{8080}{url}',
                headers={'Authorization': f'Bearer {access_token}'},
                json={**data},
            )
        except Exception as e:
            raise e

    return response
