# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.utils.const_functions import ikb


# Инлайн-клавиатура для пользователя
def user_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("Действие", data="user_inline_x"),
        ikb("Раздел", data="user_inline:user_btn"),
        ikb("Скоро", data="..."),
    ).row(
        ikb("Неизвестная кнопка", data="unknown"),
    )

    return keyboard.as_markup()


# Инлайн-клавиатура для админа
def admin_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("Действие", data="admin_inline_x"),
        ikb("Раздел", data="admin_inline:admin_btn"),
        ikb("Скоро", data="..."),
    ).row(
        ikb("Неизвестная кнопка", data="unknown"),
    )

    return keyboard.as_markup()
