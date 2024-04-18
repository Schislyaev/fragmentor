from aiogram.filters.callback_data import CallbackData

from uuid import UUID


class Confirm(CallbackData, prefix='confirmation'):
    confirmation: str
    booking_id: int
    schedule_id: UUID


class ConfirmConfirm(CallbackData, prefix='cc'):
    cc: str
    booking_id: int
    schedule_id: UUID
