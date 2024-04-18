from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from core.settings import settings

limiter = Limiter(
    get_remote_address,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri=f'redis://{settings.redis_url}:{settings.redis_port}',
)
