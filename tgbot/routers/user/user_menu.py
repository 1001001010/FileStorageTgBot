# - *- coding: utf- 8 - *-
import os
from collections import Counter
from aiogram import Router, Bot, F
from aiogram.types import Message

from tgbot.database.db_users import UserModel
from tgbot.database.db_files import Filex
from tgbot.database.db_folders import Folderx
from tgbot.keyboards.inline_file import folder_for_load, prod_item_file_swipe_fp
from tgbot.keyboards.inline_folder import user_folder
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.const_functions import ded

router = Router(name=__name__)


# Загрузка файлов
@router.message(F.text == '📤 Загрузить файлы')
async def user_button_upload_file(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()
    
    await message.answer(
        ded("""
            📁 <b>Выберите папку для загрузки:</b>
            
            🔹 Укажите, в какую папку вы хотите загрузить файлы
        """), reply_markup=folder_for_load(remover=0, user_id=User.id, parent_id=0)
    )
    
    
# Открытие файлов
@router.message(F.text == '🧮 Мои файлы')
async def user_button_my_files(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()

    files = Filex.gets(user_id=User.id)
    folders = Folderx.gets(user_id=User.id)
    extensions = [file.name.split('.')[-1] for file in files if '.' in file.name]
    counter = Counter(extensions)
    top_extensions = ', '.join(f"\n.{ext} ({count})" for ext, count in counter.most_common(5)) if extensions else "Нет файлов"

    await message.answer(
        ded(f"""
            📁 <b>Ваши файлы</b> 

            📦 <b>Всего папок:</b> <code>{len(folders)}</code> 
            🧮 <b>Всего файлов:</b> <code>{len(files)}</code> 
            🔥 <b>Популярные расширения:</b> <code>{top_extensions}</code>

            🔍 <i>Вы можете просмотреть, удалить или скачать файлы</i>
            """), reply_markup=prod_item_file_swipe_fp(0, User.id, 0)
        )


# Добавление папок
@router.message(F.text == '📁 Папки')
async def user_button_uplaod_folder(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()
    
    await message.answer(
        ded(f"""
            🌟 <b>Выберите директорию</b> для создания новой папки:
            🗂️ Вы можете выбрать любую из доступных папок или создать новую
            📂 Это поможет вам организовать файлы в удобной структуре
            """), reply_markup=user_folder(remover=0, user_id=User.id, parent_id=0)
        )