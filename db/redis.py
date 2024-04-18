# import redis
#
# from core.settings import settings
#
# redis = redis.from_url(f'redis://{settings.redis_url}:{settings.redis_port}')
import aioredis
from aioredis import Redis
from core.settings import settings


redis = aioredis.from_url(f'redis://{settings.redis_host}:{settings.redis_port}')


# Функция понадобится при внедрении зависимостей
def get_redis() -> Redis | None:
    return redis
