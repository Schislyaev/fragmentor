from pydantic import BaseModel, field_validator, FutureDatetime, ConfigDict
from zoneinfo import ZoneInfo


class Timezone(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    time_zone: str

    @field_validator('time_zone')
    def validate_and_convert_timezone(cls, v):
        if not isinstance(v, ZoneInfo):
            try:
                # Преобразование строки в ZoneInfo
                v = ZoneInfo(v)
            except Exception as e:
                raise ValueError(f"Недопустимая временная зона: {v}") from e
        return v


class TimeSlotIn(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    time_start: FutureDatetime
    time_zone: Timezone

    @field_validator('time_start')
    def validate_dt(cls, v):
        if (v.minute != 0) and (v.minute % 15 != 0):
            raise ValueError('Минуты должны быть кратны 15')
        return v


class SearchTimeIn(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    time_start: FutureDatetime
    time_finish: FutureDatetime
    time_zone: Timezone
