from contextlib import asynccontextmanager

# import aioredis
import uvicorn
from cashews import cache
from fastapi.applications import FastAPI
from fastapi.responses import JSONResponse, ORJSONResponse
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware

from AdminPanel.admin_panel import get_admin_panel
from core.fastapi_config import config
from core.settings import settings
# from core.logger import log
# from db import redis
from db.postgres import init_models, init_table  # noqa
from server.api.v11 import booking, payment, schedules, token, users, google_oauth
from starlette.middleware import Middleware


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
    docs_url=None,  # '/api/openapi',
    openapi_url=None,  # '/api/openapi.json',
    redoc_url=None,
    default_response_class=ORJSONResponse,
    openapi_tags=[
        {
            'name': 'FragMentor Backend',
            'description': 'Backend платформы FragMentor.'
        },
    ]
)


# @app.middleware("http")
# async def add_from_cache_headers(request: Request, call_next):
#     body = await request.body()  # noqa
#     response = await call_next(request)
#     return response


app.add_middleware(SessionMiddleware, secret_key="some-random-string")
app.include_router(users.router, prefix='/api/v11', tags=['USERS'])
app.include_router(token.router, prefix='/api/v11', tags=['TOKENS'])
app.include_router(schedules.router, prefix='/api/v11', tags=['SCHEDULES'])
app.include_router(booking.router, prefix='/api/v11', tags=['BOOKINGS'])
# app.include_router(create_channel.router, prefix='/api/v11', tags=['DISCORD'])
app.include_router(payment.router, prefix='/api/v11', tags=['PAYMENT'])
app.include_router(google_oauth.router, prefix='/api/v11')


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    # Запись информации об ошибке в лог
    # logging.error(f"ValueError occurred: {exc}")
    # Возврат кастомного ответа на клиент
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)}
    )

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
        ws_ping_interval=30,
        ws_ping_timeout=3000,
        # log_config=log(__name__),
        # log_level=config.log_level,
    )
