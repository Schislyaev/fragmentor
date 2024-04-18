from aiogram.fsm.state import StatesGroup, State


class StepsConfirmBooking(StatesGroup):
    GET_CONFIRMATION = State()
