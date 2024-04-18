import aioredis
from contextlib import asynccontextmanager
import uvicorn
from cashews import cache
from fastapi.applications import FastAPI
from fastapi import BackgroundTasks
from fastapi.responses import ORJSONResponse
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles

import sys
import pathlib

from core.fastapi_config import config
from core.settings import settings
# from core.logger import log
from db import redis
from db.postgres import init_models, init_table
from server.api.v11 import token, users, schedules, booking, payment
from AdminPanel.admin_panel import get_admin_panel
# from tg_services.security import JWTAuthMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # redis.redis = await aioredis.from_url(f'redis://{settings.redis_host}:{settings.redis_port}')

    # Создание таблиц (режим разработки)
    # if settings.debug:
    # if True:
    #     await init_models()
    # await init_table('bookings')
    # await init_table('payments')

    # Инициализация кэша для запросов
    cache.setup(f'redis://{settings.redis_host}:{settings.redis_port}')

    print('BDs connected')

    # Инициализация Админ панели
    admin_panel, admin_views = get_admin_panel(app=app)
    [admin_panel.add_view(admin_view) for admin_view in admin_views]
    yield


app = FastAPI(
    lifespan=lifespan,
    title=config.project_name,
    description=config.project_description,
    version=config.project_version,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    openapi_tags=[
        {
            'name': 'FragMentor Backend',
            'description': 'Backend платформы. Реализуемый в текущий момент сервис: Авторизация'
        },
    ]
)

# app.add_middleware(JWTAuthMiddleware)
# app.mount("/statics", StaticFiles(directory="statics"), name="static")
app.include_router(users.router, prefix='/api/v11', tags=['USERS'])
app.include_router(token.router, prefix='/api/v11', tags=['TOKENS'])
app.include_router(schedules.router, prefix='/api/v11', tags=['SCHEDULES'])
app.include_router(booking.router, prefix='/api/v11', tags=['BOOKINGS'])
# app.include_router(create_channel.router, prefix='/api/v11', tags=['DISCORD'])
app.include_router(payment.router, prefix='/api/v11', tags=['PAYMENT'])


# @app.middleware("http")
# async def add_from_cache_headers(request: Request, call_next):
#     """Добавляет в headers ключ, если он брался из кэша."""
#
#     with cache.detect as detector:
#         response = await call_next(request)
#         if request.method.lower() != 'get':
#             return response
#         if detector.calls:
#             response.headers['X-From-Cache-keys'] = 'cached_info'
#     return response


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8080,
        # log_config=log(__name__),
        # log_level=config.log_level,
    )
