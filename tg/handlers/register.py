from aiogram import types
from aiogram.fsm.context import FSMContext
from pydantic import ValidationError
from utils.helpers import httpx_request_get, httpx_request_patch
from utils.schemas import ValidateEmail
from utils.statesemail import StepsEmail


async def register_user(message: types.Message, state: FSMContext):
    await message.answer(f'{message.from_user.first_name}, Введи свой e-mail')
    await state.set_state(StepsEmail.GET_EMAIL)


async def get_email(message: types.Message, state: FSMContext):

    email = message.text.lower()
    tg_id = message.from_user.id
    try:
        ValidateEmail(email=email)
    except ValidationError:
        await message.answer('Введи корректный e-mail')
        return

    try:
        response = await httpx_request_get(url=f'/api/v11/user/{email}')
        if not response.status_code == 200:
            msg = 'Что то не так на сервере'
        else:
            if not response.json():
                msg = 'Вы еще не зарегистрировались на FragMentor. Зайдите на сайт для регистрации.'
            else:
                is_tg_id = response.json().get('credentials').get('tg_id')
                is_trainer = response.json().get('credentials').get('is_trainer')
                user_id = response.json().get('credentials').get('user_id')
                if is_tg_id:
                    msg = 'Ты уже с нами'
                elif not is_trainer:
                    msg = 'Ты не тренер'

                else:
                    response = await httpx_request_patch(url='/api/v11/user/update', user_id=user_id, tg_id=tg_id)
                    if response.status_code == 409:
                        msg = 'Хмм.. твой ТГ уже есть в нашей базе. Ты уже с нами с другого емейла'
                    elif response.status_code == 200:
                        msg = 'OK'
                    else:
                        msg = 'Что то не так на сервера'

    finally:
        await message.answer(msg)
        await state.clear()
        return
