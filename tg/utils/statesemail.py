from aiogram.fsm.state import State, StatesGroup


class StepsEmail(StatesGroup):
    GET_EMAIL = State()
