from aiogram import Bot
from aiogram.types import CallbackQuery
from callbacks.callbackdata import Confirm, ConfirmConfirm
from keyboards.confirm import get_confirm_confirm_keyboard
from utils.response_to_confirmation import get_is_confirmed

is_confirmed = get_is_confirmed()


async def select_confirm_booking(call: CallbackQuery, bot: Bot, callback_data: Confirm):
    confirm = callback_data.confirmation
    booking_id = callback_data.booking_id
    schedule_id = callback_data.schedule_id
    await call.message.delete_reply_markup()

    if confirm == 'да':
        await call.message.answer(
            text='ТОЧНО?\nПути назад не будет - нужно будет учить!',
            reply_markup=get_confirm_confirm_keyboard(answer=confirm, booking_id=booking_id, schedule_id=schedule_id),
            parse_mode='HTML'
        )
        await call.answer()

    elif confirm == 'нет':
        await call.message.answer(
            text='OK\nЯ удаляю это время из твоего календаря',
            parse_mode='HTML'
        )
        await call.answer()

        await is_confirmed.no(booking_id=booking_id, schedule_id=schedule_id)


async def select_confirm_confirm_bookings(call: CallbackQuery, bot: Bot, callback_data: ConfirmConfirm):
    confirm = callback_data.cc
    booking_id = callback_data.booking_id
    schedule_id = callback_data.schedule_id
    await call.message.delete_reply_markup()

    if confirm == 'точно_да':
        await call.message.answer(text='OK')
        await call.answer()

        await is_confirmed.yes(booking_id=booking_id, schedule_id=schedule_id)

    elif confirm == 'отмена':
        await call.message.answer(
            text='OK\nЯ удаляю это время из твоего календаря',
            parse_mode='HTML'
        )
        await call.answer()

        await is_confirmed.no(booking_id=booking_id, schedule_id=schedule_id)
