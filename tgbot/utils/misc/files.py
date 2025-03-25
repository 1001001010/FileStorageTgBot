import os
import hashlib
from aiogram import Bot
from tgbot.data.config import get_forbidden_extensions, get_forbidden_mime_types, PATH_FILES
from tgbot.utils.misc.encryption import encrypt_file
from tgbot.utils.const_functions import gen_id

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
    unique_id = gen_id() # Генерируем уникальный id

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