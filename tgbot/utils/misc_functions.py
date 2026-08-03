# - *- coding: utf- 8 - *-
from aiogram import Bot
from aiogram.types import FSInputFile

from tgbot.data.config import settings, get_admins
from tgbot.utils.const_functions import get_date, send_admins
from tgbot.utils.misc.bot_logging import bot_logger


# Уведомление админам после запуска
async def startup_notify(bot: Bot):
    if len(get_admins()) >= 1 and settings.status_notification:
        await send_admins(bot, "<b>✅ Бот запущен</b>")


# Автобэкап базы для админов
async def autobackup_admin(bot: Bot):
    if not settings.database_export:
        return

    for admin in get_admins():
        try:
            await bot.send_document(
                admin,
                FSInputFile(settings.database_path),
                caption=f"<b>📦 #АВТОБЭКАП | <code>{get_date()}</code></b>",
            )
        except Exception:
            bot_logger.warning("Не удалось отправить автобэкап админу %s", admin, exc_info=True)
