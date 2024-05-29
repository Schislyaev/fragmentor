import json
from functools import lru_cache
from typing import Any
from uuid import UUID

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
        username, password, re_captcha_token = form["username"], form["password"], form['g-recaptcha-response']

        url = f'http://{settings.host}:{settings.port}/api/v11/login'
        headers = {'Content-Type': 'application/json'}
        body = {
            'email': username,
            'password': password,
            'time_zone': 'Europe/Madrid',
            're_captcha_token': re_captcha_token
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
        token = json.loads(response.text).get('access_token').get('access_token')
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

    async def update_model(self, request, pk, data):
        user_id = UUID(pk)
        record = await User.get_by_id(user_id)
        data_to_update = {}
        for key in data:
            if (
                    (key != 'schedules')
                    and (key != 'bookings_as_student')
                    and (key != 'bookings_as_trainer')
                    and (key != 'photo')
            ):
                if data[key] != getattr(record, key):
                    data_to_update[key] = data[key]
        await User.update(user_id=user_id, data=data_to_update)
        return await super().update_model(request, pk, data={})


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
        base_url='/admin/3641aa34-598a-429f-b1e4-986a45b97506',
        templates_dir=settings.admin_panel_templates
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
