from aiogram.fsm.state import StatesGroup, State


class StepsEmail(StatesGroup):
    GET_EMAIL = State()
