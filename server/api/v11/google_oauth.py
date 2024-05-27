from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import JSONResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from urllib.parse import urlencode, quote
import json

from core.settings import settings
from services.user import get_service, UserService

G_CLIENT_ID = settings.google_client_id.get_secret_value()
G_CLIENT_SECRET = settings.google_client_secret.get_secret_value()

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=G_CLIENT_ID,
    client_secret=G_CLIENT_SECRET,
    client_kwargs={
        'scope': 'openid email profile',
        'redirect_url': f'https://fragmentor.website/api/v11/google/auth'
    }
)

router = APIRouter()


@router.get('/google/login')
async def login(request: Request):
    time_zone = request.query_params.get('timezone')
    request.session['time_zone'] = time_zone
    redirect_uri = str(request.url_for('auth'))
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/google/auth')
async def auth(
        request: Request,
        service: UserService = Depends(get_service)
):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token['userinfo']
        time_zone = request.session.get('time_zone')
        response = await service.login_google(user.get('email'), time_zone)
        # frontend_redirect_url = (
        #                     f"http://localhost:3000/oauth/callback?email={response.get('email')}&"
        #                     f"access_token={response.get('access_token')}&"
        #                     f"time_zone={time_zone}&"
        #                     f"is_trainer={response.get('is_trainer')}&"
        #                     f"is_email_confirmed={response.get('is_email_confirmed')}"
        # )
        frontend_redirect_url = f"https://{settings.front_host}:{settings.front_port}/oauth/callback?data={quote(json.dumps(response))}"
        return RedirectResponse(frontend_redirect_url)
        # return JSONResponse(status_code=status.HTTP_200_OK, content=response)
    except OAuthError as e:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(e)}
        )
