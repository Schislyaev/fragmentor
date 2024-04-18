# from cashews import cache
from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse
from pydantic import EmailStr

from core.settings import settings
from server.api.schemas.user import Credentials, User
from services.security import credentials_exception, oauth2_scheme, check_user
from services.user import UserService, get_service

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

router = APIRouter()


@router.post(
    path='/register',
    summary='Зарегистрировать пользователя',
    description='Получить данные email и пароль',
    response_description='Вывод статуса операции',
    # response_model=list[StoredNote],
)
# @cache(
#     ttl=settings.redis_cash_timeout,
#     key='{film_id}'
# )
async def register(
        creds: Credentials = Body(...),
        user: UserService = Depends(get_service),
):
    token = await user.register(credentials=creds)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={'token': token})


@router.post(
    path='/login',
    summary='Login пользователя',
    description='Проверить пользователя и выдать токен',
    response_description='Токен',
    # response_model=,
    # dependencies=[Depends(JWTBearer())]
)
# @cache(
#     ttl=settings.redis_cash_timeout,
#     key='{user_email}'
# )
async def login(
        token: str = Depends(oauth2_scheme),
        user: UserService = Depends(get_service),
):
    if await user.login_and_return_token(token=token):
        return JSONResponse(status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED)


@router.patch(
    path='/user/update',
    summary='Внести изменения о пользователе',
    description='Внести изменения о пользователе',
    dependencies=[Depends(oauth2_scheme)],
)
async def update_user(
        data: dict = Body(...),
        user: UserService = Depends(get_service),
):

    await user.update(**data)
    return JSONResponse(status_code=status.HTTP_200_OK, content={'message': 'ok'})


@router.get(
    path='/user/get_tg_ids',
    dependencies=[Depends(oauth2_scheme)],
)
async def get_tg_ids(
        user: UserService = Depends(get_service),
):
    tg_ids = await user.get_tg_ids()
    return tg_ids


@router.get(
    path='/user/{user_email}',
    summary='Получить пользователя',
    description='Получить данные email и пароль',
    response_description='Данные пользователя',
    response_model=User,
    # dependencies=[Depends(JWTBearer())]
)
# @cache(
#     ttl=settings.redis_cash_timeout,
#     key='{user_email}'
# )
async def get_user(
        token: str = Depends(oauth2_scheme),
        user_email: str = EmailStr,
        user: UserService = Depends(get_service),
) -> User | Exception:

    # email = await check_user(token=token)
    email = user_email
    #
    # try:
    #     payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    #     email: str = payload.get('sub')
    #     if email is None:
    #         raise credentials_exception
    # except JWTError:
    #     raise credentials_exception
    user = await user.get_user_by_email(email=email)
    if user is None:
        raise credentials_exception
    return User(
        credentials=Credentials(
            id=user.user_id,
            email=user.email,
            password=user.password,
            is_trainer=user.is_trainer,
            tg_id=user.tg_id
        ),
        token=token
    )
