from functools import lru_cache

from fastapi import HTTPException, status

from db.models.user import User
from services.security import create_access_token
from zoneinfo import ZoneInfo


class TokenService:

    @staticmethod
    async def get_token(
            email: str,
            password: str,
            time_zone: ZoneInfo = ZoneInfo("Europe/Madrid")  # :todo Correct it
    ):
        user = await User.get_by_email(email=email)
        if not (user and await User.authenticate(email=email, password=password)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not isinstance(time_zone, str):
            time_zone = time_zone.key
        access_token = create_access_token(
            data={'sub': user.email, 'time_zone': time_zone}
        )
        return {'access_token': access_token, 'token_type': 'Bearer'}


@lru_cache()
def get_token_service() -> TokenService:
    return TokenService()
