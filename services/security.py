from datetime import datetime, timedelta, timezone

import httpx
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

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

recaptcha_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate recaptcha",
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


async def check_user_get_id(token):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get('id')
        if id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return user_id


def get_payload(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception

    return payload


async def re_captcha_v3(token: str):
    secret_key = settings.google_recaptcha_key.get_secret_value()
    data = {
        'secret': secret_key,
        'response': token
    }
    async with httpx.AsyncClient(timeout=httpx.Timeout(45.0, read=30.0)) as client:
        response = await client.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = response.json()
        if result.get("success") and result.get("score") >= 0:  # Установите пороговое значение по вашему усмотрению
            # Процедура логина
            return {"message": "Logged in successfully"}
        else:
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=result,
                    headers={"WWW-Authenticate": "Bearer"},
            )


def generate_confirmation_token(email, token):
    payload = get_payload(token)
    payload['sub'] = email
    return create_access_token(payload)


def verify_confirmation_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload['sub']  # Возвращает email, если токен валиден
    except JWTError:
        return None
