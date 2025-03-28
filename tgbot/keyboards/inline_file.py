# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.database.db_files import Filex
from tgbot.database.db_folders import Folderx
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
def prod_item_file_swipe_fp(remover: int, user_id: int, parent_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_files = Filex.gets(user_id=user_id, folder_id=parent_id)
    get_folders = Folderx.gets(user_id=user_id, folder_id=parent_id)

    folders_and_files = get_files + get_folders

    if parent_id != 0:
        folder = Folderx.get(id=parent_id)
        keyboard.row(
            ikb("⬅️ Вверх", data=f"folder_and_file_open:folder:{folder.folder_id}")
        )

    for count, select in enumerate(range(remover, len(get_files))):
        if count < 10:
            user_file = get_files[select]

            keyboard.row(
                ikb(
                    user_file.name,
                    data=f"folder_and_file_open:file:{user_file.id}",
                )
            )
    for count, select in enumerate(range(remover, len(get_folders))):
        if count < 10:
            user_folders = get_folders[select]

            keyboard.row(
                ikb(
                    "📁 " + user_folders.name,
                    data=f"folder_and_file_open:folder:{user_folders.id}",
                )
            )

    buildp_kb = build_pagination_finl(folders_and_files, f"files_and_folders_swipe:{parent_id}", remover)
    keyboard.row(*buildp_kb)

    return keyboard.as_markup()


# Открытие списка папок для загрузки файла
def folder_for_load(remover: int, user_id: int, parent_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    if parent_id != 0:
        folder = Folderx.get(id=parent_id)
        keyboard.row(
            ikb("⬅️ Вверх", data=f"folder_back_upload:{folder.folder_id}"), ikb("📥 Загрузить сюда", data=f"upload_here:{parent_id}")
        )
    else:  
        keyboard.row(
            ikb("📥 Загрузить сюда", data=f"upload_here:{parent_id}"),
        )
    get_folders = Folderx.gets(user_id=user_id, folder_id=parent_id)

    for count, select in enumerate(range(remover, len(get_folders))):
        if count < 10:
            user_folders = get_folders[select]

            keyboard.row(
                ikb(
                    "📁 " + user_folders.name,
                    data=f"upload_in:{user_folders.id}",
                )
            )

    buildp_kb = build_pagination_finl(get_folders, f"folder_for_upload_swipe:{parent_id}", remover)
    keyboard.row(*buildp_kb)

    return keyboard.as_markup()



# Открытие меню управления файлом
def file_menu(file_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(
        ikb("📥 Скачать файл", data=f"file:download:{file_id}"),
    )

    keyboard.row(
        ikb("✏️ Переименовать", data=f"file:rename:{file_id}"),
        ikb("🗑️ Удалить", data=f"file:delete:{file_id}")
    )

    keyboard.row(
        ikb("⬅️ Назад", data=f"file:back:{file_id}")
    )

    return keyboard.as_markup()