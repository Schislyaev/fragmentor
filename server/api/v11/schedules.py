# from cashews import cache
from datetime import datetime, timedelta

from fastapi import (APIRouter, Body, Depends, HTTPException, Path, Response,
                     status)
from fastapi.responses import JSONResponse

from server.api.schemas.schedule import SearchTimeIn, TimeSlotIn, Timezone
from server.api.schemas.user import User
from services.schedule import ScheduleService, get_schedule
from services.security import oauth2_scheme
from services.user import UserService, get_service

router = APIRouter()


@router.post(
    path='/schedule/create',
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
    await schedule_service.add_time(**data.model_dump(), trainer_id=trainer_id)

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


@router.post(
    path='/schedule/search/token',
    summary='Получить время по тренеру',
    description='Получаем список временных слотов по токену',
    response_description='Список временных слотов',
    # dependencies=[Depends(oauth2_scheme)]
)
async def timeslots_by_trainer_token(
        schedule_service: ScheduleService = Depends(get_schedule),
        token: str = Depends(oauth2_scheme),
        user: User = Depends(get_service),
        time_zone: Timezone = Body(...),
) -> list:
    trainer = await user.get_current_user(token)

    if not trainer.is_trainer:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'message': 'Not trainer'})

    trainer_id = trainer.user_id

    schedules = await schedule_service.get_timeslots_by_trainer_id(
        trainer_id=trainer_id,
        student_time_zone=time_zone.time_zone
    )

    return schedules


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


@router.post(
    path='/schedule/search/time',
    summary='Перейти в календарь тренера',
    description='Перейти в панель календаря тренера',
    response_description='Редирект на панель календаря тренера',
    dependencies=[Depends(oauth2_scheme)]
)
async def trainers_by_timeslot(
        schedule_service: ScheduleService = Depends(get_schedule),
        data: SearchTimeIn = Body(...),
) -> JSONResponse:

    schedules = await schedule_service.get_trainers_by_timeslot(
        time_start=data.time_start,
        time_finish=data.time_finish,
        time_zone=data.time_zone.time_zone
    )

    if schedules:
        return schedules
    else:
        return JSONResponse(content=None, status_code=status.HTTP_200_OK)


@router.post(
    path='/schedule/search/all',
    summary='Получить словарь тренеров с их таймслотами',
    description='Получить словарь тренеров с их таймслотами',
    response_description='Словарь тренеров с их таймслотами',
    dependencies=[Depends(oauth2_scheme)]
)
async def trainers_dict_by_timeslot(
        schedule_service: ScheduleService = Depends(get_schedule),
        time_zone: dict = Body(...),
) -> JSONResponse:

    trainers_dict = await schedule_service.get_trainers_with_timeslots(
        time_start=datetime.now() + timedelta(hours=1),
        time_finish=datetime.now() + timedelta(weeks=480),
        time_zone=time_zone
    )

    if trainers_dict:
        return trainers_dict
    else:
        return JSONResponse(content=None, status_code=status.HTTP_200_OK)
