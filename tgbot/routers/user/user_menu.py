# - *- coding: utf- 8 - *-
import os
from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery

from tgbot.database.db_users import UserModel
from tgbot.database.db_files import Filex
from tgbot.database.db_extensions import Extensionsx
from tgbot.database.db_mime_types import MimeTypesx
from tgbot.keyboards.inline_user import abort_upload_finl
from tgbot.utils.misc.bot_models import FSM, ARS
from tgbot.utils.const_functions import ded, format_size

from tgbot.utils.misc.files import validate_file, download_file_and_generate_name, encrypt_downloaded_file, get_file_hash

router = Router(name=__name__)


@router.message(F.text == '📤 Загрузить файлы')
async def user_button_inline(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()

    await state.set_state("load_files")
    await message.answer(
        "📁 Отправьте файл для его загрузки", reply_markup=abort_upload_finl()
    )
    

@router.message(F.text == '🧮 Мои файлы')
async def user_button_inline(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()

    await message.answer(
        "Click Button - User Inline"
    )
    
    
# Отмена загрузки файла
@router.message(Command(commands=['abort_upload']))
async def cancellation(message: Message, bot: Bot, state: FSM, arSession: ARS):
    await state.clear()

    await message.answer(f"<b>Отменено</b>")
    
    
# Загрузка файла
@router.message(F.document, StateFilter('load_files'))
async def prod_position_add_file_get(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    # Проверка на запрещенные расширения и MIME типы
    validation_error = validate_file(message.document.file_name, message.document.mime_type)
    if validation_error:
        await message.answer(validation_error)
        return
    
    try:
        # Генерируем имя и скачиваем файл
        download_path, new_file_name = await download_file_and_generate_name(bot, message.document.file_id, message.document.file_name)

        # Получаем хэш файла
        file_hash = get_file_hash(download_path, hash_algorithm='sha256')

        # Проверяем наличие файла по хэшу
        existing_file = Filex.get(file_hash=file_hash, user_id=User.id)
        if existing_file:
            await message.answer(f"❌ Файл с хэшем {file_hash} уже был загружен вами!")
            return
        existing_file_other_user = Filex.get(file_hash=file_hash)
        if existing_file_other_user:
            pass

        file_extension = os.path.splitext(message.document.file_name)[1].lower()

        # Получаем или добавляем расширение в базу данных
        extension = Extensionsx.get(extension=file_extension)
        if not extension:
            Extensionsx.add(file_extension)  # Если нет, добавляем
            extension = Extensionsx.get(extension=file_extension)  # Получаем его ID

        # Получаем или добавляем MIME-тип в базу данных
        mime = MimeTypesx.get(mime_type=message.document.mime_type)
        if not mime:
            MimeTypesx.add(message.document.mime_type)  # Если нет, добавляем
            mime = MimeTypesx.get(mime_type=message.document.mime_typeype)  # Получаем его ID

        # Вставляем запись о файле в базу данных, включая ID расширения и MIME- тип
        Filex.add(
            name=message.document.file_name,
            path=download_path,
            extensions_id=extension.id,
            mime_type_id=mime.id,
            file_hash=file_hash,
            user_id=User.id,
            size=message.document.file_size
        )

        encrypted_file_path = encrypt_downloaded_file(download_path)
        await message.answer(ded(f"""
            Файл <code>{message.document.file_name}</code> ({format_size(message.document.file_size)}) успешно загружен
            """))
    except Exception as e:
        await message.answer(f"❌ Ошибка при загрузке файла: {e}")
