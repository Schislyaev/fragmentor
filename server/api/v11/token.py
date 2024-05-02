# from cashews import cache
from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm

from services.tokens import TokenService, get_token_service

router = APIRouter()


@router.post(
    path='/token',
    summary='Получить access token',
    response_description='Access token',
    # response_model=(Token, bool)
)
async def get_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        service: TokenService = Depends(get_token_service),
        time_zone: str = Body()
):

    token = await service.get_token(
        email=form_data.username,
        password=form_data.password,
        time_zone=time_zone
    )

    return token
