import json
from functools import lru_cache
from typing import Any

import httpx
from fastapi import FastAPI, Request
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend

from AdminPanel.admin_helper_models import PaymentSum, TGBroadcast
from core.settings import settings
from db.models.booking import Booking
from db.models.user import User
from db.postgres import engine
from services.security import (credentials_exception, get_password_hash,
                               get_payload)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        url = f'http://{settings.host}:{settings.port}/api/v11/login'
        headers = {'Content-Type': 'application/json'}
        body = {
            'email': username,
            'password': password,
            'time_zone': 'Europe/Madrid'
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(50000.0, read=300.0)) as client:
            try:
                response = await client.post(url=url, json=body, headers=headers)
                if response.status_code in [401, 422]:
                    raise credentials_exception
            except Exception as e:
                print(e)
                raise e

        # Вытаскиваю токен из структуры и из него payload
        token = json.loads(response.text)[0].get('access_token')
        payload = get_payload(token)
        if not payload.get('is_superuser'):
            raise credentials_exception

        # Validate username/password credentials
        # And update session
        request.session.update({"token": token})
        # request.state.auth = token
        # print(request.state)
        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        # request.state.auth = None
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        # token = request.state.auth
        if not token:
            return False

        # Check the token in depth
        return True


class UserAdmin(ModelView, model=User):
    column_list = ['user_id', 'email', 'password', 'tg_id', 'is_trainer', 'is_email_confirmed', 'created_at', 'updated_at']

    async def insert_model(self, request: Request, data: dict) -> Any:
        hashed_password = get_password_hash(data['password'])
        data['password'] = hashed_password
        return await super().insert_model(request, data)


class BookingAdmin(ModelView, model=Booking):
    column_list = ['id', 'status']


class PaymentSumAdmin(ModelView, model=PaymentSum):
    column_list = ['amount', 'created_at', 'updated_at']
    column_default_sort = [(PaymentSum.updated_at, True)]
    column_sortable_list = [PaymentSum.created_at]


class TGBroadcastAdmin(ModelView, model=TGBroadcast):
    column_list = ['id', 'message', 'created_at']
    column_default_sort = [(TGBroadcast.created_at, True)]
    column_sortable_list = [TGBroadcast.created_at]


@lru_cache()
def get_admin_panel(app: FastAPI):
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=AdminAuth(secret_key='test'),
        base_url='/admin'
    )

    # class UserAdmin(ModelView, model=User):
    #     column_list = ['user_id', 'email', 'password', 'created_at', 'updated_at']
    #
    #     async def insert_model(self, request: Request, data: dict) -> Any:
    #         hashed_password = get_password_hash(data['password'])
    #         request.session.update({"password": hashed_password})
    #         data['password'] = hashed_password
    #         return await super().insert_model(request, data)

    return admin, [UserAdmin, PaymentSumAdmin, TGBroadcastAdmin, BookingAdmin]

# admin.add_view(UserAdmin)
