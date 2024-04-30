from functools import lru_cache
from uuid import UUID

from db.models.user import User
from server.api.schemas.user import Credentials
from services.security import check_user
from services.tokens import get_token_service


class UserService:
    @staticmethod
    async def register(credentials: Credentials):
        await User.add(credentials.model_dump(exclude={'time_zone'}))

        service = get_token_service()
        token, is_trainer = await service.get_token(credentials.email, credentials.password, credentials.time_zone)

        return token, is_trainer, credentials.email

    @staticmethod
    async def get_user_by_email(email: str):
        user = await User.get_by_email(email=email)
        return user

    @staticmethod
    async def login_and_return_token(credentials: Credentials):
        service = get_token_service()
        token, is_trainer = await service.get_token(credentials.email, credentials.password, credentials.time_zone)

        return token, is_trainer, credentials.email

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

    @staticmethod
    async def get_bookings_by_email(email) -> list:
        user = await User.get_by_email(email=email)
        bookings = await User.fetch_all_bookings(user_id=user.user_id)

        return bookings

    @staticmethod
    async def get_count_of_bookings_completed(trainer_id) -> int:
        user = await User.get_by_id(trainer_id=trainer_id)

        condition = {'status': 'completed'}
        bookings = await User.fetch_all_bookings(user_id=user.user_id, conditions=condition)

        return len(bookings)

    @staticmethod
    async def get_user_by_id(user_id):
        user = await User.get_by_id(user_id)

        return user


@lru_cache()
def get_service() -> UserService:
    return UserService()
