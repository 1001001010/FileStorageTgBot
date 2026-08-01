# - *- coding: utf- 8 - *-
from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, Message

from tgbot.database import ModelUsers
from tgbot.utils.const_functions import del_message
from tgbot.utils.misc.bot_models import FSM, ARS

router = Router(name=__name__)


# Колбэк для удаления текущего сообщения
@router.callback_query(F.data == 'close_this')
async def main_callback_close(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: ModelUsers):
    await del_message(call.message)


# Колбэк-заглушка для пустых кнопок
@router.callback_query(F.data == '...')
async def main_callback_answer(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: ModelUsers):
    await call.answer(cache_time=30)


# Ответ на колбэк, который никто не обработал
@router.callback_query()
async def main_callback_missed(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: ModelUsers):
    await call.answer(f"❗️ Неизвестный колбэк: {call.data}", True)


# Ответ на неизвестные сообщения
@router.message()
async def main_message_missed(message: Message, bot: Bot, state: FSM, arSession: ARS, User: ModelUsers):
    await message.answer(
        "♦️ Неизвестная команда\n"
        "♦️ Введите /start",
    )
