from functools import lru_cache
from uuid import UUID

from db.models.user import User
from server.api.schemas.user import Credentials
from services.security import check_user
from services.tokens import get_token_service


class UserService:
    @staticmethod
    async def register(credentials: Credentials):
        await User.add(credentials.dict(exclude={'time_zone'}))

        service = get_token_service()
        token = await service.get_token(credentials.email, credentials.password, credentials.time_zone)

        return token

    @staticmethod
    async def get_user_by_email(email: str):
        user = await User.get_by_email(email=email)
        return user

    @staticmethod
    async def login_and_return_token(token: str):
        if token := token:
            return True
        else:
            return False

    @staticmethod
    async def get_current_user(token: str):

        email = await check_user(token=token)
        user = await User.get_by_email(email=email)

        return user

    @staticmethod
    async def update(user_id: UUID, **data):
        user = await User.update(user_id=user_id, data=data)
        return user

    @staticmethod
    async def get_tg_ids() -> list:
        tg_ids = await User.fetch_all_tg_ids()
        return tg_ids


@lru_cache()
def get_service() -> UserService:
    return UserService()
