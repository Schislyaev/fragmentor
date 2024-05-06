from uuid import UUID
from zoneinfo import ZoneInfo

import orjson
from pydantic import BaseModel, ConfigDict, EmailStr, constr, field_validator


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Credentials(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: UUID | None = None
    email: EmailStr
    password: constr(min_length=4)
    is_trainer: bool = False
    time_zone: str = 'Europe/Berlin'
    tg_id: int | None = None
    re_captcha_token: str | None = None

    @field_validator('time_zone')
    def validate_and_convert_timezone(cls, v):
        if not isinstance(v, ZoneInfo):
            try:
                # Преобразование строки в ZoneInfo
                v = ZoneInfo(v)
            except Exception as e:
                raise ValueError(f"Недопустимая временная зона: {v}") from e
        return v


class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    credentials: Credentials
    token: str
