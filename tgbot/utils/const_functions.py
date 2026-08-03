# - *- coding: utf- 8 - *-
import html
import secrets
import string
import textwrap
import time
from datetime import datetime
from typing import List, Optional, Union

from aiogram import Bot
from aiogram.types import (InlineKeyboardButton, KeyboardButton, WebAppInfo, Message, InlineKeyboardMarkup,
                           ReplyKeyboardMarkup)
from pytz import timezone

from tgbot.data.config import get_admins, settings
from tgbot.utils.misc.bot_logging import bot_logger


#################################### AIOGRAM ###################################
# Быстрая сборка реплай-кнопки
def rkb(text: str) -> KeyboardButton:
    return KeyboardButton(text=text)


# Быстрая сборка инлайн-кнопки
def ikb(
        text: str,
        data: Optional[str] = None,
        url: Optional[str] = None,
        switch: Optional[str] = None,
        web: Optional[str] = None,
) -> InlineKeyboardButton:
    if data is not None:
        return InlineKeyboardButton(text=text, callback_data=data)
    elif url is not None:
        return InlineKeyboardButton(text=text, url=url)
    elif switch is not None:
        return InlineKeyboardButton(text=text, switch_inline_query=switch)
    elif web is not None:
        return InlineKeyboardButton(text=text, web_app=WebAppInfo(url=web))
    else:
        raise ValueError("Не указано действие для инлайн-кнопки")


# Удаление сообщения без падения на ошибках Telegram
async def del_message(message: Message):
    try:
        await message.delete()
    except Exception:
        bot_logger.debug("Не удалось удалить сообщение", exc_info=True)


# Отправка текста с фото, если оно передано или обычным сообщением
async def smart_message(
        bot: Bot,
        user_id: int,
        text: str,
        keyboard: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None,
        photo: Optional[str] = None,
):
    if photo is not None and photo.title() != "None":
        await bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=text,
            reply_markup=keyboard,
        )
    else:
        await bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=keyboard,
        )


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
        except Exception:
            bot_logger.warning("Не удалось отправить сообщение админу %s", admin, exc_info=True)


################################## РАЗНОЕ ######################################
# Убирает лишние отступы в многострочном тексте
def ded(get_text: str) -> str:
    return textwrap.dedent(get_text or "").strip()


# Чистит HTML-символы, чтобы Telegram не сломал разметку
def clear_html(get_text: str) -> str:
    return html.escape(get_text or "", quote=False)


# Убирает пустые и мусорные элементы из списка
def clear_list(get_list: list) -> list:
    trash = {"", " ", ".", ",", "\r", "\n"}

    return [value for value in get_list if value not in trash]


# Делит список на части нужного размера
def split_list(get_list: list, count: int) -> List[list]:
    return [get_list[i:i + count] for i in range(0, len(get_list), count)]


# Возвращает текущую дату, при full=True еще и время
def get_date(full: bool = True) -> str:
    bot_timezone = timezone(settings.timezone)

    if full:
        return datetime.now(bot_timezone).strftime("%d.%m.%Y %H:%M:%S")
    else:
        return datetime.now(bot_timezone).strftime("%d.%m.%Y")


# Возвращает Unix-время: секунды или наносекунды
def get_unix(full: bool = False) -> int:
    if full:
        return time.time_ns()
    else:
        return int(time.time())


# Конвертирует дату в Unix и обратно
def convert_date(from_time, full=True, second=True) -> Union[str, int]:
    bot_timezone = timezone(settings.timezone)
    from_time = str(from_time).strip().replace("-", ".")

    if from_time.isdigit():
        from_timestamp = int(from_time)
        if full:
            to_time = datetime.fromtimestamp(from_timestamp, bot_timezone).strftime("%d.%m.%Y %H:%M:%S")
        elif second:
            to_time = datetime.fromtimestamp(from_timestamp, bot_timezone).strftime("%d.%m.%Y %H:%M")
        else:
            to_time = datetime.fromtimestamp(from_timestamp, bot_timezone).strftime("%d.%m.%Y")
    else:
        parts = from_time.split()

        if len(parts) == 2 and ":" in parts[0]:
            time_part, date_part = parts
        elif len(parts) == 2:
            date_part, time_part = parts
        else:
            date_part, time_part = from_time, "00:00:00"

        date_values = date_part.split(".")
        time_values = time_part.split(":")

        if len(time_values) == 2:
            time_values.append("0")

        if len(date_values[0]) == 4:
            x_year, x_month, x_day = date_values[0], date_values[1], date_values[2]
        else:
            x_day, x_month, x_year = date_values[0], date_values[1], date_values[2]

        date_time = datetime(
            int(x_year),
            int(x_month),
            int(x_day),
            int(time_values[0]),
            int(time_values[1]),
            int(time_values[2]),
        )
        date_time = bot_timezone.localize(date_time)
        to_time = int(date_time.timestamp())

    return to_time


# Генерация числового уникального ID
def gen_id(len_id: int = 16) -> int:
    if len_id <= 0:
        raise ValueError("Длина ID должна быть больше нуля")

    first_digit = secrets.choice("123456789")
    other_digits = "".join(secrets.choice(string.digits) for _ in range(len_id - 1))

    return int(f"{first_digit}{other_digits}")


# Генерация пароля под разные сценарии
def gen_password(len_password: int = 16, type_password: str = "default") -> str:
    if len_password <= 0:
        raise ValueError("Длина пароля должна быть больше нуля")

    if type_password == "default":
        alphabet = string.ascii_letters + string.digits
    elif type_password == "letter":
        alphabet = string.ascii_letters
    elif type_password == "number":
        alphabet = string.digits
    elif type_password == "onechar":
        alphabet = string.digits
    else:
        raise ValueError("Неизвестный тип пароля")

    random_chars = "".join(secrets.choice(alphabet) for _ in range(len_password))

    if type_password == "onechar":
        random_chars = f"{secrets.choice(string.ascii_letters)}{random_chars[1:]}"

    return random_chars


# Склоняет единицы времени под число
def convert_times(get_time: int, get_type: str = "day") -> str:
    get_time = int(get_time)
    if get_time < 0: get_time = 0

    if get_type == "second":
        get_list = ['секунда', 'секунды', 'секунд']
    elif get_type == "minute":
        get_list = ['минута', 'минуты', 'минут']
    elif get_type == "hour":
        get_list = ['час', 'часа', 'часов']
    elif get_type == "day":
        get_list = ['день', 'дня', 'дней']
    elif get_type == "month":
        get_list = ['месяц', 'месяца', 'месяцев']
    else:
        get_list = ['год', 'года', 'лет']

    if get_time % 10 == 1 and get_time % 100 != 11:
        count = 0
    elif 2 <= get_time % 10 <= 4 and (get_time % 100 < 10 or get_time % 100 >= 20):
        count = 1
    else:
        count = 2

    return f"{get_time} {get_list[count]}"


# Приводит строку или число к bool
def is_bool(value: Union[bool, str, int]) -> bool:
    value = str(value).strip().lower()

    if value in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif value in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError(f"Некорректное bool-значение: {value}")


################################### ЧИСЛА ######################################
# Приводит число к читаемой строке без лишних нулей
def snum(amount: Union[int, float], remains: int = 2) -> str:
    format_str = "{:." + str(remains) + "f}"
    str_amount = format_str.format(float(amount))

    if remains != 0:
        if "." in str_amount:
            remains_find = str_amount.find(".")
            remains_save = remains_find + 8 - (8 - remains) + 1

            str_amount = str_amount[:remains_save]

    if "." in str(str_amount):
        while str(str_amount).endswith('0'): str_amount = str(str_amount)[:-1]

    if str(str_amount).endswith('.'): str_amount = str(str_amount)[:-1]

    return str(str_amount)


# Приводит входное значение к int или float
def to_float(get_number, remains: int = 2) -> Union[int, float]:
    value = str(get_number).strip().replace(" ", "").replace(",", ".")
    number = round(float(value), remains)

    if number.is_integer():
        return int(number)

    return number


# Округляет число до int
def to_int(get_number: float) -> int:
    if "," in str(get_number):
        get_number = str(get_number).replace(",", ".")

    get_number = int(round(float(get_number)))

    return get_number


# Проверяет, является ли значение числом
def is_number(get_number: Union[str, int, float]) -> bool:
    if str(get_number).isdigit():
        return True
    else:
        if "," in str(get_number): get_number = str(get_number).replace(",", ".")

        try:
            float(get_number)
            return True
        except (TypeError, ValueError):
            return False


# Форматирует число с разделением тысяч
def format_rate(amount: Union[float, int], around: int = 2) -> str:
    value = str(amount).strip().replace(" ", "").replace(",", ".")
    number = round(float(value), around)
    response = f"{number:,.{around}f}".replace(",", " ")

    if "." in response:
        response = response.rstrip("0").rstrip(".")

    return response
