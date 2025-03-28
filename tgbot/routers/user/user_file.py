# - *- coding: utf- 8 - *-
import os
from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery

from tgbot.database.db_users import UserModel
from tgbot.database.db_files import Filex
from tgbot.database.db_extensions import Extensionsx
from tgbot.database.db_mime_types import MimeTypesx
from tgbot.keyboards.inline_file import prod_item_file_swipe_fp, folder_for_load, abort_upload_finl
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.misc.files import encrypt_downloaded_file
from tgbot.utils.const_functions import ded, format_size

from tgbot.utils.misc.files import validate_file, download_file_and_generate_name, get_file_hash

router = Router(name=__name__)
    
    
# Загрузка файла
@router.message(F.document, StateFilter('load_files'))
async def user_upload_file(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    validation_error = validate_file(message.document.file_name, message.document.mime_type)
    if validation_error:
        await message.answer(validation_error)
        return
    
    try:
        download_path, new_file_name = await download_file_and_generate_name(bot, message.document.file_id, message.document.file_name)
        file_hash = get_file_hash(download_path, hash_algorithm='sha256')
        existing_file = Filex.get(file_hash=file_hash, user_id=User.id)
        if existing_file:
            await message.answer(f"❌ Файл <code>{message.document.file_name}</code> уже был загружен вами!")
            return
        existing_file_other_user = Filex.get(file_hash=file_hash)
        if existing_file_other_user:
            pass

        file_extension = os.path.splitext(message.document.file_name)[1].lower()
        extension = Extensionsx.get(extension=file_extension)
        if not extension:
            Extensionsx.add(file_extension)
            extension = Extensionsx.get(extension=file_extension)

        mime = MimeTypesx.get(mime_type=message.document.mime_type)
        if not mime:
            MimeTypesx.add(message.document.mime_type)
            mime = MimeTypesx.get(mime_type=message.document.mime_type)

        Filex.add(
            name=message.document.file_name,
            path=download_path,
            extensions_id=extension.id,
            mime_type_id=mime.id,
            file_hash=file_hash,
            user_id=User.id,
            size=message.document.file_size,
            folder_id=(await state.get_data())['parent_id']
        )
        
        encrypted_file_path = encrypt_downloaded_file(download_path)
        await message.answer(ded(f"""
            Файл <code>{message.document.file_name}</code> ({format_size(message.document.file_size)}) успешно загружен
            """))
    except Exception as e:
        await message.answer(f"❌ Ошибка при загрузке файла: {e}")


# Отмена загрузки файла
@router.callback_query(F.data == 'abort_upload')
async def user_abort_upload(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()
    
    await call.message.delete()
    await call.message.answer(f"<b>Отменено</b>")
    
    
# Страница файлов
@router.callback_query(F.data.startswith("files_swipe:"))
async def user_buy_category_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    remover = int(call.data.split(":")[1])

    await call.message.edit_reply_markup(reply_markup=prod_item_file_swipe_fp(remover, User.id))
    
    
# Страница папок при загрузке файлов
@router.callback_query(F.data.startswith("folder_for_upload_swipe:"))
async def user_buy_category_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    remover = int(call.data.split(":")[2])
    parent_id = int(call.data.split(":")[1])

    await call.message.edit_reply_markup(reply_markup=folder_for_load(remover, User.id, parent_id))
    
    
# Переход в папку для загрузки файла
@router.callback_query(F.data.startswith("upload_in:"))
async def user_buy_category_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    parent_id = int(call.data.split(":")[1])

    await call.message.edit_reply_markup(reply_markup=folder_for_load(0, User.id, parent_id))
    

# Возвращение в папку
@router.callback_query(F.data.startswith("folder_back_upload:"))
async def user_folder_back(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    parent_id = int(call.data.split(":")[1])
    await call.message.delete()
    
    await call.message.answer(
        ded("""
            📁 <b>Выберите папку для загрузки:</b>
            
            🔹 Укажите, в какую папку вы хотите загрузить файлы
        """), reply_markup=folder_for_load(remover=0, user_id=User.id, parent_id=parent_id)
    )
    
    
# Загрузка в папку
@router.callback_query(F.data.startswith("upload_here:"))
async def user_folder_back(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    parent_id = int(call.data.split(":")[1])
    await call.message.delete()
    
    await state.update_data(parent_id=parent_id) 
    await state.set_state("load_files")
    await call.message.answer(
        "📁 Отправьте файл для его загрузки", reply_markup=abort_upload_finl()
    )
    
    
# Дейсвтия с файлами
@router.callback_query(F.data.startswith("upload_here:"))
async def user_folder_back(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    parent_id = int(call.data.split(":")[1])
    await call.message.delete()
    
    await state.update_data(parent_id=parent_id) 
    await state.set_state("load_files")
    await call.message.answer(
        "📁 Отправьте файл для его загрузки", reply_markup=abort_upload_finl()
    )