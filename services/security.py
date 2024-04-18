from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
# from starlette.middleware.base import BaseHTTPMiddleware
# from fastapi.middleware import Middleware
# # from starlette.requests import Request
# from tg_services.user import get_service

from core.settings import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v11/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def check_user(token):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return email


def get_payload(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception

    return payload


# class JWTAuthMiddleware(BaseHTTPMiddleware):
#
#     def __init__(self, app):
#         super().__init__(app)
#
#     async def dispatch(
#             self,
#             request: Request,
#             call_next,
#     ):
#         try:
#             token = request.session.get('token')
#             # token = request.state.auth
#             email = await check_user(token)
#
#             user_service = get_service()
#             user = user_service.get_user_by_email(email)
#
#             request.state.user = user
#         except Exception as e:
#             pass
#         response = await call_next(request)
#         return response
