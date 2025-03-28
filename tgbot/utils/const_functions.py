# - *- coding: utf- 8 - *-
import time
import pytz
import uuid
import random
from aiogram import Bot
from typing import Union
from datetime import datetime
from aiogram.types import KeyboardButton, Message, InlineKeyboardButton

from tgbot.data.config import get_admins, BOT_TIMEZONE


# Генерация реплай кнопки
def rkb(text: str) -> KeyboardButton:
    return KeyboardButton(text=text)


# Удаление отступов в многострочной строке ("""text""")
def ded(get_text: str) -> str:
    if get_text is not None:
        split_text = get_text.split("\n")
        if split_text[0] == "": split_text.pop(0)
        if split_text[-1] == "": split_text.pop()
        save_text = []

        for text in split_text:
            while text.startswith(" "):
                text = text[1:].strip()

            save_text.append(text)
        get_text = "\n".join(save_text)
    else:
        get_text = ""

    return get_text


# Получение текущего unix времени (True - время в наносекундах, False - время в секундах)
def get_unix(full: bool = False) -> int:
    if full:
        return time.time_ns()
    else:
        return int(time.time())
    
    
# Получение текущей даты (True - дата с временем, False - дата без времени)
def get_date(full: bool = True) -> str:
    if full:
        return datetime.now(pytz.timezone(BOT_TIMEZONE)).strftime("%d.%m.%Y %H:%M:%S")
    else:
        return datetime.now(pytz.timezone(BOT_TIMEZONE)).strftime("%d.%m.%Y")
    
# Генерация уникального айди
def gen_id(len_id: int = 16) -> int:
    mac_address = uuid.getnode()
    time_unix = int(str(time.time_ns())[:len_id])
    random_int = int(''.join(random.choices('0123456789', k=len_id)))

    return mac_address + time_unix + random_int


# Очистка текста от HTML тэгов ('<b>test</b>' -> *b*test*/b*)
def clear_html(get_text: str) -> str:
    if get_text is not None:
        if "</" in get_text: get_text = get_text.replace("<", "*")
        if "<" in get_text: get_text = get_text.replace("<", "*")
        if ">" in get_text: get_text = get_text.replace(">", "*")
    else:
        get_text = ""

    return get_text


# Удаление сообщения с обработкой ошибки от телеграма
async def del_message(message: Message):
    try:
        await message.delete()
    except:
        ...
        
        
# Отправка сообщения всем админам
async def send_admins(bot: Bot, text: str, markup=None, not_me=0):
    for admin in get_admins():
        try:
            if str(admin) != str(not_me):
                await bot.send_message(
                    admin,
                    text,
                    reply_markup=markup,
                    disable_web_page_preview=True,
                )
        except:
            ...
            
            
# Генерация инлайн кнопки
def ikb(
        text: str,
        data: str = None,
        url: str = None,
        copy: str = None,
        login: str = None,
) -> InlineKeyboardButton:
    if data is not None:
        return InlineKeyboardButton(text=text, callback_data=data)
    elif url is not None:
        return InlineKeyboardButton(text=text, url=url)
    elif copy is not None:
        return InlineKeyboardButton(text=text, copy_text=CopyTextButton(text=copy))
    
    
# Форматирование размера файлов
def format_size(size: int) -> str:
    """Форматирует размер в байты, КБ, МБ, ГБ и ТБ."""
    units = ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']
    index = 0
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    return f"{size:.2f} {units[index]}"


# Конвертация unix в дату и даты в unix
def convert_date(from_time, full=True, second=True) -> Union[str, int]:
    from tgbot.data.config import BOT_TIMEZONE

    if "-" in str(from_time):
        from_time = from_time.replace("-", ".")

    if str(from_time).isdigit():
        if full:
            to_time = datetime.fromtimestamp(from_time, pytz.timezone(BOT_TIMEZONE)).strftime("%d.%m.%Y %H:%M:%S")
        elif second:
            to_time = datetime.fromtimestamp(from_time, pytz.timezone(BOT_TIMEZONE)).strftime("%d.%m.%Y %H:%M")
        else:
            to_time = datetime.fromtimestamp(from_time, pytz.timezone(BOT_TIMEZONE)).strftime("%d.%m.%Y")
    else:
        if " " in str(from_time):
            cache_time = from_time.split(" ")

            if ":" in cache_time[0]:
                cache_date = cache_time[1].split(".")
                cache_time = cache_time[0].split(":")
            else:
                cache_date = cache_time[0].split(".")
                cache_time = cache_time[1].split(":")

            if len(cache_date[0]) == 4:
                x_year, x_month, x_day = cache_date[0], cache_date[1], cache_date[2]
            else:
                x_year, x_month, x_day = cache_date[2], cache_date[1], cache_date[0]

            x_hour, x_minute, x_second = cache_time[0], cache_time[1], cache_time[2]

            from_time = f"{x_day}.{x_month}.{x_year} {x_hour}:{x_minute}:{x_second}"
        else:
            cache_date = from_time.split(".")

            if len(cache_date[0]) == 4:
                x_year, x_month, x_day = cache_date[0], cache_date[1], cache_date[2]
            else:
                x_year, x_month, x_day = cache_date[2], cache_date[1], cache_date[0]

            from_time = f"{x_day}.{x_month}.{x_year}"

        if " " in str(from_time):
            to_time = int(datetime.strptime(from_time, "%d.%m.%Y %H:%M:%S").timestamp())
        else:
            to_time = int(datetime.strptime(from_time, "%d.%m.%Y").timestamp())

    return to_time