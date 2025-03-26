# - *- coding: utf- 8 - *-
from enum import Enum
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.database.db_folders import Folderx
from tgbot.utils.const_functions import ikb
from tgbot.keyboards.inline_helper import build_pagination_finl

class FolderBackVariants(Enum):
    BACK = "back"
    CANCEL = "cancel"


# Открытие списка главной дирректории папок пользователя
def user_folder(remover: int, user_id: int, parent_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    if parent_id != 0:
        folder = Folderx.get(id=parent_id)
        keyboard.row(
            ikb("✏️ Редактировать", data=f"folder_edit:{parent_id}")
        ),
        keyboard.row(
            ikb("⬅️ Вверх", data=f"folder_open:{folder.folder_id}"), ikb("➕ Создать папку здесь", data=f"folder_create:{parent_id}")
        )
    else:  
        keyboard.row(
            ikb("➕ Создать здесь", data=f"folder_create:{parent_id}"),
        )
    
    get_folders = Folderx.gets(user_id=user_id, folder_id=parent_id)

    for count, select in enumerate(range(remover, len(get_folders))):
            if count < 10:
                user_folder = get_folders[select]
                
                keyboard.row(
                    ikb(
                        "📁" + user_folder.name,
                        data=f"folder_open:{user_folder.id}",
                    )
                )

    buildp_kb = build_pagination_finl(get_folders, f"folder_swipe", remover)
    keyboard.row(*buildp_kb)

    return keyboard.as_markup()


def inl_user_folder_back(parent_id: int, variant: FolderBackVariants) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(
        ikb({
                FolderBackVariants.BACK: "⬅️ Назад",
                FolderBackVariants.CANCEL: "❌ Отменить"
            }[variant],
            data=f"folder_back:{parent_id}"),
    )
        
    return keyboard.as_markup()