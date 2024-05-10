from functools import lru_cache
from uuid import UUID

from fastapi import status
from fastapi.responses import JSONResponse

from db.models.user import User
from server.api.schemas.user import Credentials
from services.security import check_user, verify_confirmation_token
from services.tokens import get_token_service


class UserService:
    @staticmethod
    async def register(credentials: Credentials):
        await User.add(credentials.model_dump(exclude={'time_zone', 're_captcha_token'}))

        service = get_token_service()
        token, is_trainer, is_email_confirmed = await service.get_token(
            credentials.email,
            credentials.password,
            credentials.time_zone
        )

        # return token, is_trainer, credentials.email
        return {
            'access_token': token,
            'is_trainer': is_trainer,
            'email': credentials.email,
            'is_email_confirmed': is_email_confirmed
        }

    @staticmethod
    async def get_user_by_email(email: str):
        user = await User.get_by_email(email=email)
        return user

    @staticmethod
    async def login_and_return_token(credentials: Credentials):
        service = get_token_service()
        token, is_trainer, is_email_confirmed = await service.get_token(
            credentials.email,
            credentials.password,
            credentials.time_zone
        )

        # return token, is_trainer, credentials.email
        return {
            'access_token': token,
            'is_trainer': is_trainer,
            'email': credentials.email,
            'is_email_confirmed': is_email_confirmed
        }

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

    async def confirm_email_return_token(self, email_token):

        token_service = get_token_service()

        email = verify_confirmation_token(email_token)
        if not email:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Invalid or expired token'}
            )
        user = await self.get_user_by_email(email)
        await self.update(user_id=user.user_id, is_email_confirmed=True)

        token = await token_service.update_token(email_token)

        return {
            'access_token': token,
            'is_trainer': user.is_trainer,
            'email': email,
            'is_email_confirmed': user.is_email_confirmed
        }


@lru_cache()
def get_service() -> UserService:
    return UserService()
