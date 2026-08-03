# - *- coding: utf- 8 - *-
import asyncio
import sys

import colorama
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from tgbot.data.config import settings, get_admins, validate_bot_config
from tgbot.database.core import close_database
from tgbot.database.repository import prepare_database
from tgbot.middlewares import register_all_middlewares
from tgbot.routers import register_all_routers
from tgbot.services.api_session import AsyncRequestSession
from tgbot.utils.misc.bot_commands import set_commands
from tgbot.utils.misc.bot_logging import bot_logger
from tgbot.utils.misc_functions import autobackup_admin, startup_notify

# Включаем мгновенный вывод print() без flush=True в каждом вызове
def configure_console_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(line_buffering=True, write_through=True)


scheduler = AsyncIOScheduler(timezone=settings.timezone)
configure_console_output()
colorama.init()

# Запуск задач по расписанию
async def scheduler_start(bot):
    if settings.database_export:
        scheduler.add_job(
            autobackup_admin,
            trigger="cron",
            hour=0,
            args=(bot,),
            id="autobackup_admin",
            replace_existing=True,
            coalesce=True,
            misfire_grace_time=60,
        )

    if not scheduler.running:
        scheduler.start()


# Запуск бота и базовой обвязки
async def main():
    validate_bot_config()
    await prepare_database()  # Проверка готовности БД

    dp = Dispatcher()  # Диспетчер событий
    arSession = AsyncRequestSession()  # Общая сессия aiohttp

    bot = Bot(  # Образ Бота
        token=settings.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        ),
    )

    register_all_middlewares(dp)  # Подключение мидлварей
    register_all_routers(dp)  # Подключение роутера

    try:
        await set_commands(bot)  # Обновление команды в Telegram
        await startup_notify(bot)  # Сообщаем админам о старте
        await scheduler_start(bot)  # Подключение задач по расписанию

        bot_info = await bot.get_me()
        bot_logger.info("Бот запущен: @%s", bot_info.username)
        print(colorama.Fore.LIGHTYELLOW_EX + f"~~~~~ Бот запущен - @{bot_info.username} ~~~~~")
        print(colorama.Fore.LIGHTBLUE_EX + "~~~~~ TG developer - @lll10010010 ~~~~~")
        print(colorama.Fore.RESET)

        if len(get_admins()) == 0:
            print("***** УКАЖИТЕ BOT_ADMIN_IDS В .env *****")

        await bot.delete_webhook()  # Сбрасывание вебхука, если он был
        await bot.get_updates(offset=-1)  # Чистка старых апдейтов

        # Запуск бота (polling режим)
        await dp.start_polling(
            bot,
            arSession=arSession,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)

        await arSession.close()  # Закрытие сессии aiohttp
        await bot.session.close()  # Закрытие сессии API Telegram
        await close_database()  # Закрытие соединений с БД


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        bot_logger.warning("Бот остановлен")
