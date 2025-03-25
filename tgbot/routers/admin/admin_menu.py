# - *- coding: utf- 8 - *-
import os

import aiofiles
from datetime import datetime, timedelta
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message, CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder

from tgbot.data.config import PATH_DATABASE, PATH_LOGS
from tgbot.database.db_users import UserModel, Userx
from tgbot.database.db_files import Filex
from tgbot.database.db_extensions import Extensionsx
from tgbot.database.db_mime_types import MimeTypesx
from tgbot.utils.const_functions import get_date, ded
from tgbot.utils.misc.bot_models import FSM, ARS

router = Router(name=__name__)

# Получение Базы Данных
@router.message(Command(commands=['db', 'database']))
async def admin_database(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()

    await message.answer_document(
        FSInputFile(PATH_DATABASE),
        caption=f"<b>📦 #BACKUP | <code>{get_date()}</code></b>",
    )


# Получение логов
@router.message(Command(commands=['log', 'logs']))
async def admin_log(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()

    media_group = MediaGroupBuilder(
        caption=f"<b>🖨 #LOGS | <code>{get_date(full=False)}</code></b>",
    )

    if os.path.isfile(PATH_LOGS):
        media_group.add_document(media=FSInputFile(PATH_LOGS))

    if os.path.isfile("tgbot/data/sv_log_err.log"):
        media_group.add_document(media=FSInputFile("tgbot/data/sv_log_err.log"))

    if os.path.isfile("tgbot/data/sv_log_out.log"):
        media_group.add_document(media=FSInputFile("tgbot/data/sv_log_out.log"))

    await message.answer_media_group(media=media_group.build())


# Очистить логи
@router.message(Command(commands=['clear_log', 'clear_logs', 'log_clear', 'logs_clear']))
async def admin_logs_clear(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()

    if os.path.isfile(PATH_LOGS):
        async with aiofiles.open(PATH_LOGS, "w") as file:
            await file.write(f"{get_date()} | LOGS WAS CLEAR")

    if os.path.isfile("tgbot/data/sv_log_err.log"):
        async with aiofiles.open("tgbot/data/sv_log_err.log", "w") as file:
            await file.write(f"{get_date()} | LOGS WAS CLEAR")

    if os.path.isfile("tgbot/data/sv_log_out.log"):
        async with aiofiles.open("tgbot/data/sv_log_out.log", "w") as file:
            await file.write(f"{get_date()} | LOGS WAS CLEAR")

    await message.answer("<b>🖨 Логи были очищены</b>")
    

# Статистика
@router.message(F.text == '📊 Статистика')
async def admin_stats(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    
    # Получение даты начала месяца и дня в Unix-форате
    now = datetime.now()
    start_of_month = int(datetime(now.year, now.month, 1).timestamp())
    start_of_day = int(datetime(now.year, now.month, now.day).timestamp())
    
    await message.answer(ded(f"""📊 <b>Статистика</b> на <code>{get_date()}</code>

                                 <b>Пользователи:</b>
                                 👤 Всего: <code>{len(Userx.get_all())}</code>
                                 📅 За месяц: <code>{len(Userx.get_by_period(start_of_month))}</code>
                                 🌅 За день: <code>{len(Userx.get_by_period(start_of_day))}</code>
 
                                 <b>Файлы:</b>
                                 📁 Всего: <code>{len(Filex.get_all())}</code>
                                 📅 За месяц: <code>{len(Filex.get_by_period(start_of_month))}</code>
                                 🌅 За день: <code>{len(Filex.get_by_period(start_of_day))}</code>

                                 🛠️ Уникальных расширений: <code>{len(Extensionsx.get_all())}</code>
                                 🔖 Уникальных MIME-типов: <code>{len(MimeTypesx.get_all())}</code>
                                 """))
