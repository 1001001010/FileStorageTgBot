# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.database.db_files import Filex
from tgbot.utils.const_functions import ikb
from tgbot.keyboards.inline_helper import build_pagination_finl


# Отмена загрузки файла
def abort_upload_finl() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb("❌ Отмена", data="abort_upload"),
    )

    return keyboard.as_markup()


# Открытие списка файлов
def prod_item_file_swipe_fp(remover: int, user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_files = Filex.gets(user_id=user_id)

    for count, select in enumerate(range(remover, len(get_files))):
        if count < 10:
            user_file = get_files[select]

            keyboard.row(
                ikb(
                    user_file.name,
                    data=f"file_open:{user_file.id}",
                )
            )

    buildp_kb = build_pagination_finl(get_files, f"files_swipe", remover)
    keyboard.row(*buildp_kb)

    return keyboard.as_markup()