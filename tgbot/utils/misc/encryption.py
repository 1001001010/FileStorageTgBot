import os
import colorama
from cryptography.fernet import Fernet

from tgbot.data.config import ENCRYPTION_KEY


# Генерация ключа
def generate_encryption_key(key_path=ENCRYPTION_KEY):
    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, "wb") as key_file:
            key_file.write(key)
        print(colorama.Fore.LIGHTBLUE_EX + "Новый ключ шифрования сгенерирован")
    else:
        print(colorama.Fore.GREEN + "Ключ шифрования уже существует")


# Загрузка ключа
def load_key(key_path=ENCRYPTION_KEY):
    if not os.path.exists(key_path):
        raise FileNotFoundError("Ключ шифрования не найден")

    with open(key_path, "rb") as key_file:
        key = key_file.read()

    return Fernet(key)


# Шифрование файла
def encrypt_file(file_path, key_path=ENCRYPTION_KEY):
    if not os.path.exists(file_path):
        return None

    try:
        cipher = load_key(key_path)
        
        with open(file_path, "rb") as f:
            data = f.read()

        encrypted_data = cipher.encrypt(data)

        enc_path = f"{file_path}.enc"
        with open(enc_path, "wb") as f:
            f.write(encrypted_data)

        os.remove(file_path)

        return enc_path

    except:
        ...


# Расшифровка файла
def decrypt_file(encrypted_path, key_path=ENCRYPTION_KEY):
    if not os.path.exists(encrypted_path):
        print(colorama.Fore.RED + f"Файл {encrypted_path} не найден!")
        return None

    try:
        cipher = load_key(key_path)

        with open(encrypted_path, "rb") as f:
            encrypted_data = f.read()

        decrypted_data = cipher.decrypt(encrypted_data)

        decrypted_path = encrypted_path.replace(".enc", "")
        with open(decrypted_path, "wb") as f:
            f.write(decrypted_data)

        return decrypted_path

    except:
        ...