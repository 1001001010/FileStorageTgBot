# - *- coding: utf- 8 - *-
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from tgbot.data.config import get_admins
from tgbot.utils.const_functions import rkb


# Кнопки главного меню
def menu_frep(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.row(
        rkb("📤 Загрузить"), rkb("📂 Мои файлы")
    )
    keyboard.row(
        rkb("🔗 Общие ссылки"), rkb("⭐ Избранное")
    )
    keyboard.row(
        rkb("🔍 Поиск"), rkb("📊 Хранилище")
    )
    keyboard.row(
        rkb("🗑 Корзина"), rkb("⚙️ Настройки"),
    )
    keyboard.row(
        rkb("❓ Помощь")
    )

    # if user_id in get_admins():
    #     keyboard.row(
    #         rkb("Админ-меню"),
    #     )

    return keyboard.as_markup(resize_keyboard=True)
