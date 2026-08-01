# - *- coding: utf- 8 - *-
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from tgbot.database.db_users import UserModel
from tgbot.keyboards.inline_main import user_finl
from tgbot.keyboards.reply_main import menu_frep
from tgbot.utils.misc.bot_models import FSM, ARS

router = Router(name=__name__)


# Кнопка пользовательского меню
@router.message(F.text == 'Пользовательское меню')
async def user_button_inline(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()

    await message.answer(
        "Инлайн-клавиатура пользователя",
        reply_markup=user_finl()
    )


# Команда возврата в меню
@router.message(Command(commands="menu"))
async def user_command_menu(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()

    await message.answer(
        "Команда /menu открывает главное меню",
        reply_markup=menu_frep(message.from_user.id),
    )


# Колбэк для демо-действия
@router.callback_query(F.data == 'user_inline_x')
async def user_callback_inline_x(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await call.answer("Действие выполнено")


# Колбэк с параметром из пользовательской кнопки
@router.callback_query(F.data.startswith('user_inline:'))
async def user_callback_inline(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    get_data = call.data.split(":")[1]

    await call.answer(f"Выбран раздел: {get_data}", True)
