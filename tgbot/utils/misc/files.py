import os
import shutil
import hashlib
from aiogram import Bot
from aiogram.types import FSInputFile
from tgbot.data.config import get_forbidden_extensions, get_forbidden_mime_types, PATH_FILES
from tgbot.utils.misc.encryption import encrypt_file, decrypt_file
from tgbot.utils.const_functions import gen_id, ded, format_size, convert_date
from tgbot.keyboards.inline_file import file_menu

# Валидация файлов
def validate_file(file_name: str, mime_type: str) -> str:
    file_extension = os.path.splitext(file_name)[1].lower()

    forbidden_extensions = get_forbidden_extensions()
    forbidden_mime_types = get_forbidden_mime_types()

    if file_extension in forbidden_extensions:
        return f"❌ Загрузка файла с расширением <code>{file_extension}</code> запрещена"
    
    if mime_type in forbidden_mime_types:
        return f"❌ Загрузка файла с MIME типом <code>{mime_type}</code> запрещена"
    
    return None


async def download_file_and_generate_name(bot: Bot, file_id: str, file_name: str) -> str:
    unique_id = gen_id()

    file_extension = os.path.splitext(file_name)[1].lower()
    new_file_name = f"{unique_id}{file_extension}"
    
    file = await bot.get_file(file_id)
    file_path = file.file_path
    download_path = f"{PATH_FILES}/{new_file_name}"
    os.makedirs(os.path.dirname(download_path), exist_ok=True)

    await bot.download_file(file_path, download_path)
    return download_path, new_file_name


def encrypt_downloaded_file(download_path: str) -> str:
    encrypted_file_path = encrypt_file(download_path)
    return encrypted_file_path


def get_file_hash(file_path: str, hash_algorithm: str = 'sha256') -> str:
    hash_func = getattr(hashlib, hash_algorithm)()

    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(64 * 1024):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        print(f"Ошибка при вычислении хэша файла: {e}")
        return None
    

async def send_decrypted_file(bot, chat_id, file_info, extention):
    enc_file_path = f"{file_info.path}.enc"

    if not os.path.isfile(enc_file_path):
        await bot.send_message(chat_id, "❌ Файл не найден!")
        return

    decrypted_path = decrypt_file(enc_file_path)

    temp_path = os.path.join(os.path.dirname(decrypted_path), file_info.name)
    shutil.move(decrypted_path, temp_path)

    await bot.send_document(
        chat_id=chat_id,
        document=FSInputFile(temp_path),
        caption=ded(f"""
            📄 <b>Информация о файле:</b> <i>{file_info.name}</i> 
            
            🔖 <b>Расширение:</b> <code>{extention.extension}</code>
            📏 <b>Размер:</b> <code>{format_size(file_info.size)}</code>
            🗓️ <b>Дата загрузки:</b> <code>{convert_date(file_info.created_at)}</code>
        """),
        reply_markup=file_menu(file_id=file_info.id)
    )

    try:
        os.remove(temp_path)
    except Exception:
        ...