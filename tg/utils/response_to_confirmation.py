from fastapi.responses import JSONResponse, Response
from uuid import UUID
import httpx
from functools import lru_cache
from core.settings import settings


class IsConfirmed:
    @staticmethod
    async def yes(booking_id: int, schedule_id: UUID):
        # Передаем на создание платежа
        async with httpx.AsyncClient(timeout=httpx.Timeout(45.0, read=30.0)) as client:
            try:
                response = await client.post(
                    url=f'http://{settings.host}:{settings.port}/api/v11/payment/create_payment',
                    json={'booking_id': booking_id, 'schedule_id': str(schedule_id)}
                )
                return Response(status_code=response.status_code)
            except Exception as e:
                raise e

    @staticmethod
    async def no(booking_id: int, schedule_id: UUID):
        # Передаем на отмену брони
        async with httpx.AsyncClient(timeout=httpx.Timeout(45.0, read=30.0)) as client:
            try:
                response = await client.post(
                    url=f'http://{settings.host}:{settings.port}/api/v11/booking/cancel',
                    json={'booking_id': booking_id, 'schedule_id': str(schedule_id)}
                )
                return Response(status_code=response.status_code)
            except Exception as e:
                raise e


@lru_cache()
def get_is_confirmed() -> IsConfirmed:
    return IsConfirmed()

