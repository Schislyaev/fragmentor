# from cashews import cache
import uuid

from fastapi import APIRouter, Body, Depends, status, HTTPException, Response, Path
from fastapi.responses import JSONResponse
from jose import JWTError, jwt

from core.settings import settings
from server.api.schemas.user import Credentials, User
from services.security import credentials_exception, oauth2_scheme, check_user
from services.user import UserService, get_service
from services.schedule import ScheduleService, get_schedule
from server.api.schemas.schedule import TimeSlotIn, Timezone

router = APIRouter()


@router.post(
    path='/schedule',
    summary='Перейти в календарь тренера',
    description='Перейти в панель календаря тренера',
    response_description='Редирект на панель календаря тренера',
    # response_model=list[StoredNote],
    # dependencies=[Depends(JWTBearer())]
)
# @cache(
#     ttl=settings.redis_cash_timeout,
#     key='{film_id}'
# )
async def schedule_create(
        token: str = Depends(oauth2_scheme),
        user: UserService = Depends(get_service),
        schedule_service: ScheduleService = Depends(get_schedule),
        data: TimeSlotIn = Body(...)
):
    trainer = await user.get_current_user(token)

    if not trainer.is_trainer:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'message': 'Not trainer'})

    trainer_id = trainer.user_id
    await schedule_service.add_time(**data.dict(), trainer_id=trainer_id)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={'message': 'Time added'})


@router.delete(
    path='/schedule/delete',
    summary='Перейти в календарь тренера',
    description='Перейти в панель календаря тренера',
    response_description='Редирект на панель календаря тренера',
    dependencies=[Depends(oauth2_scheme)]
)
async def schedule_delete(
        schedule_service: ScheduleService = Depends(get_schedule),
        data: dict = Body()
):
    record_id = data.get('record_id')
    await schedule_service.delete_time(record_id=record_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    path='/schedule/search/trainer/{trainer_id}',
    summary='Получить время по тренеру',
    description='Получаем список временных слотов по id тренера',
    response_description='Список временных слотов',
    dependencies=[Depends(oauth2_scheme)]
)
async def timeslots_by_trainer_id(
        schedule_service: ScheduleService = Depends(get_schedule),
        time_zone: Timezone = Body(...),
        trainer_id: str = Path()
) -> list:

    schedules = await schedule_service.get_timeslots_by_trainer_id(
        trainer_id=trainer_id,
        student_time_zone=time_zone.time_zone
    )

    return schedules


@router.get(
    path='/schedule/search/time/{time}',
    summary='Перейти в календарь тренера',
    description='Перейти в панель календаря тренера',
    response_description='Редирект на панель календаря тренера',
    dependencies=[Depends(oauth2_scheme)]
)
async def trainers_by_timeslot(
        schedule_service: ScheduleService = Depends(get_schedule),
        time_zone: Timezone = Body(...),
        time: str = Path()
) -> JSONResponse:

    schedules = await schedule_service.get_trainers_by_timeslot(timeslot=time, student_time_zone=time_zone.time_zone)

    if schedules:
        msg = {'msg': [str(schedule) for schedule in schedules]}
    else:
        msg = {'msg': 'В это время никого нет'}

    return JSONResponse(content=msg, status_code=status.HTTP_200_OK)

