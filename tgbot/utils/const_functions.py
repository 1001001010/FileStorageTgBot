# - *- coding: utf- 8 - *-
import time
from datetime import datetime
import pytz
from aiogram import Bot
from aiogram.types import KeyboardButton, Message

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