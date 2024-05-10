# from cashews import cache
from zoneinfo import ZoneInfo

import magic
from fastapi import (APIRouter, Body, Depends, File, HTTPException, UploadFile,
                     status)
from fastapi.responses import JSONResponse, Response
from pydantic import EmailStr

from core.settings import settings
from notifications.email_notification import EmailSender, get_email_service
from server.api.schemas.user import Credentials, User
from services.security import (check_user, credentials_exception,
                               generate_confirmation_token, oauth2_scheme,
                               re_captcha_v3)
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
    re_captcha_token = creds.re_captcha_token

    if not await re_captcha_v3(re_captcha_token):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={'detail': 'Привет, углеродный брат. Ты - не кожаный мешок..'}
        )

    response = await user.register(credentials=creds)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=response)


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
        creds: Credentials = Body(...),
        user: UserService = Depends(get_service),
):
    re_captcha_token = creds.re_captcha_token
    if not await re_captcha_v3(re_captcha_token):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Привет, углеродный брат. Ты - не кожаный мешок.."}
        )
    response = await user.login_and_return_token(credentials=creds)
    if response['access_token']:
        return JSONResponse(status_code=status.HTTP_200_OK, content=response)
    else:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Incorrect username or password"}
        )


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
    try:
        await user.update(**data)
        return JSONResponse(status_code=status.HTTP_200_OK, content={'message': 'ok'})
    except HTTPException as e:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={'detail': str(e)})


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
            user_id=user.user_id,
            email=user.email,
            password=user.password,
            is_trainer=user.is_trainer,
            tg_id=user.tg_id
        ),
        token=token
    )


@router.post(
    path='/booking/list',
    summary='Вывести брони по тренеру',
    description='Список броней',
    response_description='Список броней',
    response_model=None
    # dependencies=[Depends(oauth2_scheme)]
)
# @cache(
#     ttl=settings.redis_cash_timeout,
#     key='{film_id}'
# )
async def booking_list(
        user: UserService = Depends(get_service),
        token: str = Depends(oauth2_scheme),
        # data: dict = Body(...)
) -> list:
    email = await check_user(token)
    bookings = await user.get_bookings_by_email(email=email)

    bookings_list = [
        {
            'id': booking.id,
            'time': booking.time_start.astimezone(ZoneInfo(booking.time_zone_trainer)),
            'status': booking.status
        } for booking in bookings
    ]
    return bookings_list


@router.post(
    path='/booking/count_completed',
    summary='Вывести количество завершенных броней по тренеру',
    description='Количество броней',
    response_description='Количество броней',
    dependencies=[Depends(oauth2_scheme)],
)
# @cache(
#     ttl=settings.redis_cash_timeout,
#     key='{film_id}'
# )
async def booking_counts(
        user: UserService = Depends(get_service),
        data: dict = Body(...),
) -> int:
    trainer_id = data.get('trainer_id')
    count = await user.get_count_of_bookings_completed(trainer_id=trainer_id)

    return count


@router.patch(
    path='/user/upload_photo',
    response_class=Response
)
async def upload_photo(
        service: UserService = Depends(get_service),
        token: str = Depends(oauth2_scheme),
        photo: UploadFile = File(...),
):
    try:
        photo_data = await photo.read()
        user = await service.get_current_user(token=token)
        await service.update(user.user_id, photo=photo_data)
        return JSONResponse(status_code=status.HTTP_200_OK, content={'message': 'ok'})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': str(e)})


@router.post(
    path='/user/get_photo',
    dependencies=[Depends(oauth2_scheme)],
)
async def get_photo(
        service: UserService = Depends(get_service),
        data: dict = Body(...),
):
    try:
        trainer_id = data.get('trainer_id')
        user = await service.get_user_by_id(user_id=trainer_id)
        if not user.photo:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        mime = magic.Magic(mime=True)
        content_type = mime.from_buffer(user.photo)  # Определяю content-type

        return Response(content=user.photo, media_type=content_type)
    except Exception as e:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post(
    path='/user/get_photo_by_token',
)
async def get_photo_by_token(
        service: UserService = Depends(get_service),
        token: str = Depends(oauth2_scheme),
):
    try:
        user = await service.get_current_user(token=token)
        if not user.photo:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        mime = magic.Magic(mime=True)
        content_type = mime.from_buffer(user.photo)  # Определяю content-type

        return Response(content=user.photo, media_type=content_type)
    except Exception as e:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post(
    path='/user/verify_email/update_user'
)
async def verify_email_update(
        data: dict = Body(...),
        service: UserService = Depends(get_service)
):
    email_token = data.get('token')

    response = await service.confirm_email_return_token(email_token)

    return JSONResponse(status_code=status.HTTP_200_OK, content=response)


@router.post(
    path='/user/verify_email/generate_url'
)
async def verify_email(
        token: str = Depends(oauth2_scheme),
        email: EmailSender = Depends(get_email_service),
):
    user_email = await check_user(token)
    verification_token = generate_confirmation_token(user_email, token)
    token_url = f'http://{settings.front_host}:{settings.front_port}/verify/{verification_token}'

    await email.send(
        message_id=1,
        subject='Подтверждение e-mail',
        destinations=[user_email, 'pschhhh@gmail.com'],
        message=f'Подтверди свою почту пройдя по этой ссылке:\n{token_url}'
    )
