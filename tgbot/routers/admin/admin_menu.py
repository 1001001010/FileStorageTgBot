# - *- coding: utf- 8 - *-
from pathlib import Path

import aiofiles
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message, CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder

from tgbot.data.config import BOT_DATABASE_EXPORT, PATH_DATABASE, PATH_LOGS
from tgbot.database.db_users import UserModel
from tgbot.keyboards.inline_main import admin_finl
from tgbot.utils.const_functions import get_date
from tgbot.utils.misc.bot_models import FSM, ARS

router = Router(name=__name__)
LOGS_DIR = Path(PATH_LOGS).parent
SERVICE_LOG_FILES = (
    LOGS_DIR / "sv_log_err.log",
    LOGS_DIR / "sv_log_out.log",
)


# Кнопка админского меню
@router.message(F.text == 'Админ-меню')
async def admin_button_inline(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()

    await message.answer(
        "Инлайн-клавиатура админа",
        reply_markup=admin_finl()
    )


# Колбэк для демо-действия админа
@router.callback_query(F.data == 'admin_inline_x')
async def admin_callback_inline_x(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await call.answer("Админское действие выполнено")


# Колбэк с параметром из админской кнопки
@router.callback_query(F.data.startswith('admin_inline:'))
async def admin_callback_inline(call: CallbackQuery, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    get_data = call.data.split(":")[1]

    await call.answer(f"Выбран админский раздел: {get_data}", True)


# Отправка файла базы админам
@router.message(Command(commands=['db', 'database']))
async def admin_database(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()

    if not BOT_DATABASE_EXPORT:
        await message.answer("<b>📦 Экспорт базы данных отключён в настройках</b>")
        return

    if not Path(PATH_DATABASE).is_file():
        await message.answer("<b>📦 Файл базы данных не найден</b>")
        return

    await message.answer_document(
        FSInputFile(PATH_DATABASE),
        caption=f"<b>📦 #БЭКАП | <code>{get_date()}</code></b>",
    )


# Отправка логов админам
@router.message(Command(commands=['log', 'logs']))
async def admin_log(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()

    log_files = []

    if Path(PATH_LOGS).is_file():
        log_files.append(PATH_LOGS)

    for log_file in SERVICE_LOG_FILES:
        if log_file.is_file():
            log_files.append(str(log_file))

    caption = f"<b>🖨 #ЛОГИ | <code>{get_date(full=False)}</code></b>"

    if len(log_files) == 0:
        await message.answer("<b>🖨 Логи не найдены</b>")
    elif len(log_files) == 1:
        await message.answer_document(FSInputFile(log_files[0]), caption=caption)
    else:
        media_group = MediaGroupBuilder(caption=caption)

        for log_file in log_files:
            media_group.add_document(media=FSInputFile(log_file))

        await message.answer_media_group(media=media_group.build())


# Очистка файлов логов
@router.message(Command(commands=['clear_log', 'clear_logs', 'log_clear', 'logs_clear']))
async def admin_logs_clear(message: Message, bot: Bot, state: FSM, arSession: ARS, User: UserModel):
    await state.clear()

    log_files = [Path(PATH_LOGS), *SERVICE_LOG_FILES]

    for log_file in log_files:
        if not log_file.is_file():
            continue

        async with aiofiles.open(log_file, "w", encoding="utf-8") as file:
            await file.write(f"{get_date()} | ЛОГИ ОЧИЩЕНЫ")

    await message.answer("<b>🖨 Логи очищены</b>")
