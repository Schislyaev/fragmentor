from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import JSONResponse, RedirectResponse
from urllib.parse import quote
import json
import httpx

from core.settings import settings
from services.user import get_service, UserService

Y_CLIENT_ID = settings.yandex_client_id.get_secret_value()
Y_CLIENT_SECRET = settings.yandex_client_secret.get_secret_value()

router = APIRouter()


@router.get('/yandex/login')
async def login(request: Request):
    time_zone = request.query_params.get('timezone')
    request.session['time_zone'] = time_zone

    auth_url = (
        "https://oauth.yandex.ru/authorize?"
        f"response_type=code&client_id={Y_CLIENT_ID}&redirect_uri=http://localhost:8080/api/v11/yandex/auth"
    )
    return RedirectResponse(auth_url)


@router.get(path='/yandex/auth')
async def auth(
        code: str,
        request: Request,
        service: UserService = Depends(get_service),
):
    try:
        token_url = "https://oauth.yandex.ru/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": Y_CLIENT_ID,
            "client_secret": Y_CLIENT_SECRET,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            tokens = response.json()

        access_token = tokens.get("access_token")
        user_info_url = "https://login.yandex.ru/info"

        async with httpx.AsyncClient() as client:
            user_info = await client.get(user_info_url, headers={"Authorization": f"Bearer {access_token}"})
            user_data = user_info.json()

        time_zone = request.session.get('time_zone')
        response = await service.login_oauth(user_data.get('default_email'), time_zone)

        frontend_redirect_url = f"https://{settings.front_host}/oauth/callback?data={quote(json.dumps(response))}"
        # frontend_redirect_url = f"http://localhost:3000/oauth/callback?data={quote(json.dumps(response))}"
        return RedirectResponse(frontend_redirect_url)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(e)}
        )
