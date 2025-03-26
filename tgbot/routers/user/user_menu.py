# - *- coding: utf- 8 - *-
import os
from collections import Counter
from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery

from tgbot.database.db_users import UserModel
from tgbot.database.db_files import Filex
from tgbot.database.db_extensions import Extensionsx
from tgbot.database.db_mime_types import MimeTypesx
from tgbot.keyboards.inline_user import abort_upload_finl, prod_item_file_swipe_fp
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.const_functions import ded, format_size

from tgbot.utils.misc.files import validate_file, download_file_and_generate_name, encrypt_downloaded_file, get_file_hash

router = Router(name=__name__)


# Загрузка файлов
@router.message(F.text == '📤 Загрузить файлы')
async def user_button_inline(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()

    await state.set_state("load_files")
    await message.answer(
        "📁 Отправьте файл для его загрузки", reply_markup=abort_upload_finl()
    )
    

# Отмена загрузки файла
@router.callback_query(F.data == 'abort_upload')
async def user_callback_inline_x(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()
    
    await call.message.delete()
    await call.message.answer(f"<b>Отменено</b>")
    
    
# Открытие файлов
@router.message(F.text == '🧮 Мои файлы')
async def user_button_inline(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()

    files = Filex.gets(user_id=User.id)
    extensions = [file.name.split('.')[-1] for file in files if '.' in file.name]
    counter = Counter(extensions)
    top_extensions = ', '.join(f"\n.{ext} ({count})" for ext, count in counter.most_common(5)) if extensions else "Нет файлов"

    await message.answer(
        ded(f"""
            📁 <b>Ваши файлы</b> 

            📦 <b>Всего файлов:</b> <code>{len(files)}</code> 
            🔥 <b>Популярные расширения:</b> <code>{top_extensions}</code>

            🔍 <i>Вы можете просмотреть, удалить или скачать файлы.</i>
        """), reply_markup=prod_item_file_swipe_fp(0, User.id)
    )


# Загрузка файла
@router.message(F.document, StateFilter('load_files'))
async def prod_position_add_file_get(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
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
            size=message.document.file_size
        )

        await message.answer(ded(f"""
            Файл <code>{message.document.file_name}</code> ({format_size(message.document.file_size)}) успешно загружен
            """))
    except Exception as e:
        await message.answer(f"❌ Ошибка при загрузке файла: {e}")


# Страница файлов
@router.callback_query(F.data.startswith("files_swipe:"))
async def user_buy_category_swipe(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    remover = int(call.data.split(":")[1])

    await call.message.edit_reply_markup(reply_markup=prod_item_file_swipe_fp(remover, User.id))