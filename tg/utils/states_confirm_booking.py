from aiogram.fsm.state import State, StatesGroup


class StepsConfirmBooking(StatesGroup):
    GET_CONFIRMATION = State()
