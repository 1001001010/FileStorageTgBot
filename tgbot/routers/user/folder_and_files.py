# - *- coding: utf- 8 - *-
import os
from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from tgbot.database.db_users import UserModel
from tgbot.database.db_files import Filex
from tgbot.database.db_extensions import Extensionsx
from tgbot.database.db_folders import Folderx
from tgbot.keyboards.inline_file import prod_item_file_swipe_fp, file_menu, back_to_file, \
    del_file
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc.files import send_decrypted_file
from tgbot.utils.const_functions import ded, format_size, convert_date

router = Router(name=__name__)


# Открытие папки, либо файла
@router.callback_query(F.data.startswith("folder_and_file_open:"))
async def open_folder_or_file(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    ftype = str(call.data.split(":")[1])
    data = int(call.data.split(":")[2])
    if ftype == 'folder':
        await call.message.edit_reply_markup(reply_markup=prod_item_file_swipe_fp(0, User.id, data))
    elif ftype == 'file':
        file_info = Filex.get(id=data)
        await call.message.delete()
        await call.message.answer(
            ded(f"""
                📄 <b>Информация о файле:</b> <i>{file_info.name + file_info.extension}</i> 
                
                🔖 <b>Расширение:</b> <code>{file_info.extension}</code>
                📏 <b>Размер:</b> <code>{format_size(file_info.size)}</code>
                🗓️ <b>Дата загрузки:</b> <code>{convert_date(file_info.created_at)}</code>
                """), reply_markup=file_menu(file_id=file_info.id)
            )


# Свайп страниц папок и файлов
@router.callback_query(F.data.startswith("files_and_folders_swipe:"))
async def user_folder_back(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    remover = int(call.data.split(":")[2])
    parent_id = int(call.data.split(":")[1])

    await call.message.edit_reply_markup(reply_markup=prod_item_file_swipe_fp(remover, User.id, parent_id))
    
    
# Действия с файлом
@router.callback_query(F.data.startswith("file:"))
async def file_action(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    ftype = str(call.data.split(":")[1])
    file_info = Filex.get(id=call.data.split(":")[2])
    extention = Extensionsx.get(id=file_info.extensions_id)
    await call.message.delete()
    
    if ftype == 'download':
        await send_decrypted_file(bot, call.message.chat.id, file_info, extention)
    elif ftype == 'rename': 
        await state.update_data(file_id=file_info.id) 
        await state.set_state("rename_file")
        await call.message.answer(
            ded(f"""
                ✏️ <b>Введите новое название для файла:</b>
                
                📄 <b>Текущее название:</b> <code>{file_info.name}</code>""")
            )
    elif ftype == "delete":
        await call.message.answer(
            ded(f"""
                ⚠️ <b>Вы уверены</b>, что хотите удалить файл:   
                🗑️ <code>{file_info.name}{file_info.extension}</code>?"""), reply_markup=del_file(file_info.id)
            )

        

# Получение нового имени файла
@router.message(F.text, StateFilter("rename_file"))
async def user_enter_file_name(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    file_id = (await state.get_data())['file_id']
    
    Filex.update(
        file_id=file_id,
        name=message.text
    )
    
    await message.answer(
        ded(f"""
            ✅ <b>Файл успешно переименован!</b>
            
            🆕 <b>Новое название:</b> <code>{message.text}</code>"""), reply_markup=back_to_file(file_id)
        )
    

# Подтверждение удаления файла
@router.callback_query(F.data.startswith("delete_file:"))
async def file_action(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    file_id = int(call.data.split(":")[1])
    Filex.delete(id=file_id)
    
    await call.message.edit_text('🗑️ <b>Файл успешно удален!</b>')