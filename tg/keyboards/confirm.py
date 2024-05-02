from uuid import UUID

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from tg.callbacks.callbackdata import Confirm, ConfirmConfirm


def get_select_confirm_keyboard(booking_id: int, schedule_id: UUID) -> InlineKeyboardMarkup:
    select_confirm = InlineKeyboardBuilder()
    select_confirm.button(
        text='ДА',
        callback_data=Confirm(
            confirmation='да',
            booking_id=booking_id,
            schedule_id=schedule_id
        )
    )
    select_confirm.button(
        text='НЕТ',
        callback_data=Confirm(
            confirmation='нет',
            booking_id=booking_id,
            schedule_id=schedule_id
        )
    )
    select_confirm.adjust(2)

    return select_confirm.as_markup()


def get_confirm_confirm_keyboard(answer: str, booking_id: int, schedule_id: UUID) -> InlineKeyboardMarkup:
    text = 'ДА' if answer == 'да' else 'Точно НЕТ'
    callback_data = ConfirmConfirm(
        cc='точно_да' if answer == 'да' else 'точно_нет',
        booking_id=booking_id,
        schedule_id=schedule_id
    )

    select_confirm = InlineKeyboardBuilder()
    select_confirm.button(
        text=text,
        callback_data=callback_data
    )
    select_confirm.button(
        text='Отмена',
        callback_data=ConfirmConfirm(
            cc='отмена',
            booking_id=booking_id,
            schedule_id=schedule_id
        )
    )

    return select_confirm.as_markup()
