from typing import Any
from functools import lru_cache

from sqladmin import Admin, ModelView
from fastapi import FastAPI, Request

from db.postgres import engine
from db.models.user import User
from AdminPanel.admin_helper_models import PaymentSum, TGBroadcast

from services.security import get_password_hash
from sqladmin.authentication import AuthenticationBackend
import httpx
from core.settings import settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        url = f'http://{settings.host}:{settings.port}/api/v11/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        body = {'username': username, 'password': password}
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, read=30.0)) as client:
            try:
                response = await client.post(url=url, data=body, headers=headers)
            except Exception as e:
                print(e)
                raise e

        token = response.content.decode('utf-8')
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
    column_list = ['user_id', 'email', 'password', 'created_at', 'updated_at']

    async def insert_model(self, request: Request, data: dict) -> Any:
        hashed_password = get_password_hash(data['password'])
        data['password'] = hashed_password
        return await super().insert_model(request, data)


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

    return admin, [UserAdmin, PaymentSumAdmin, TGBroadcastAdmin]

# admin.add_view(UserAdmin)
