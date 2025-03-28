# - *- coding: utf- 8 - *-
import os
from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery

from tgbot.database.db_users import UserModel
from tgbot.database.db_folders import Folderx
from tgbot.keyboards.inline_folder import inl_user_folder_back, FolderBackVariants, user_folder
from tgbot.utils.const_functions import ded
from tgbot.utils.misc.bot_models import FSM, ARS

router = Router(name=__name__)


# Создание папки
@router.callback_query(F.data.startswith("folder_create:"))
async def user_upload_folder(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    parent_id = int(call.data.split(":")[1])
    await call.message.delete()
    await state.update_data(parent_id=parent_id) 
    await state.set_state("folder_name")
    await call.message.answer(
        ded("""
            🌟 <b>Создание новой папки:</b>
            
            🔹 Введите название для папки, чтобы организовать файлы по категориям.
            """), reply_markup=inl_user_folder_back(parent_id=parent_id, variant=FolderBackVariants.CANCEL)
        )


# Открытие папки
@router.callback_query(F.data.startswith("folder_open:"))
async def user_open_folder(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    folder = int(call.data.split(":")[1])
    await call.message.delete()
    
    await call.message.answer(
        ded(f"""
            🌟 <b>Выберите директорию</b> для создания новой папки:
            🗂️ Вы можете выбрать любую из доступных папок или создать новую
            📂 Это поможет вам организовать файлы в удобной структуре
            """), reply_markup=user_folder(remover=0, user_id=User.id, parent_id=folder)
    )


# Ввод имени папки
@router.message(F.text, StateFilter("folder_name"))
async def user_buy_count(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    parent_id = (await state.get_data())['parent_id']
    
    Folderx.add(
        name=message.text,
        user_id=User.id,
        folder_id=parent_id
    )
    
    # await state.clear()
    await message.answer("Папка успешно создана", reply_markup=inl_user_folder_back(parent_id=parent_id, variant=FolderBackVariants.BACK))
    

# Возвращение в папку
@router.callback_query(F.data.startswith("folder_back:"))
async def user_folder_back(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    parent_id = int(call.data.split(":")[1])
    await call.message.delete()
    
    await call.message.answer(
        ded(f"""
            🌟 <b>Выберите директорию</b> для создания новой папки:
            🗂️ Вы можете выбрать любую из доступных папок или создать новую
            📂 Это поможет вам организовать файлы в удобной структуре
            """), reply_markup=user_folder(remover=0, user_id=User.id, parent_id=parent_id)
        )
    

# Редактирование папки
@router.callback_query(F.data.startswith("folder_edit:"))
async def user_folder_back(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    folder_id = int(call.data.split(":")[1])
    await call.message.delete()
    
    await state.update_data(folder_id=folder_id) 
    await state.set_state("new_folder_name")
    await call.message.answer(
        ded("""
            📂 <b>Введите новое название папки:</b>
            
            Пожалуйста, укажите название для вашей новой папки, чтобы организовать файлы по категориям 📁
            """), reply_markup=inl_user_folder_back(parent_id=folder_id, variant=FolderBackVariants.CANCEL)
        )
    
    
# Редактирование названия папки
@router.message(F.text, StateFilter("new_folder_name"))
async def user_buy_count(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    folder_id = (await state.get_data())['folder_id']
    await state.clear()
        
    Folderx.update(
        folder_id=folder_id,
        name=message.text
    )

    await message.answer("Название успешно изменено")
    

# Страница папок
@router.callback_query(F.data.startswith("folder_swipe:"))
async def user_buy_category_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    remover = int(call.data.split(":")[2])
    parent_id = int(call.data.split(":")[1])

    await call.message.edit_reply_markup(reply_markup=user_folder(remover, User.id, parent_id))