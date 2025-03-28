# - *- coding: utf- 8 - *-
import configparser

from apscheduler.schedulers.asyncio import AsyncIOScheduler

config = configparser.ConfigParser()
config.read("settings.ini")

# Токен бота
BOT_TOKEN = configparser.ConfigParser()
BOT_TOKEN.read("settings.ini")
BOT_TOKEN = BOT_TOKEN['settings']['bot_token'].strip().replace(' ', '')

# Пути к файлам
PATH_DATABASE = "tgbot/data/database.db"  # Путь к БД
PATH_LOGS = "tgbot/data/logs.log"  # Путь к Логам
PATH_FILES = "./files"  # Путь к загруженным файлам
ENCRYPTION_KEY = "./tgbot/data/encryption_key.key"  # Путь к ключу шифрования

# Образы и конфиги
BOT_STATUS_NOTIFICATION = False  # Оповещение админам о запуске бота (True или False)
BOT_TIMEZONE = "Europe/Moscow"  # Временная зона бота
BOT_SCHEDULER = AsyncIOScheduler(timezone=BOT_TIMEZONE)  # Образ шедулера

# Получение запрещенных расширений
def get_forbidden_extensions() -> list[str]:
    forbidden_extensions = config.get('forbidden_file_types', 'forbidden_extensions')
    return [ext.strip() for ext in forbidden_extensions.split(',')]

# Получение запрещенных MIME-типов
def get_forbidden_mime_types() -> list[str]:
    forbidden_mime_types = config.get('forbidden_file_types', 'forbidden_mime_types')
    return [mime.strip() for mime in forbidden_mime_types.split(',')]

# Получение администраторов бота
def get_admins() -> list[int]:
    admins = config['settings']['admin_id'].strip().replace(" ", "")
    
    if "," in admins:
        admins = admins.split(",")
    else:
        if len(admins) >= 1:
            admins = [admins]
        else:
            admins = []

    while "" in admins: admins.remove("")
    while " " in admins: admins.remove(" ")
    while "," in admins: admins.remove(",")
    while "\r" in admins: admins.remove("\r")
    while "\n" in admins: admins.remove("\n")

    return list(map(int, admins))