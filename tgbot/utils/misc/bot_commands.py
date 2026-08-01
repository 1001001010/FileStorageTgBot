# - *- coding: utf- 8 - *-
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from tgbot.data.config import BOT_DATABASE_EXPORT, get_admins
from tgbot.utils.misc.bot_logging import bot_logger

# Команды для обычных пользователей
user_commands = [
    BotCommand(command="start", description="♻️ Перезапуск бота"),
    BotCommand(command="menu", description="🌀 Получение клавиатуры"),
]

# Команды для админов
admin_commands = [
    BotCommand(command="start", description="♻️ Перезапуск бота"),
    BotCommand(command="menu", description="🌀 Получение клавиатуры"),
    BotCommand(command="log", description="🖨 Получить логи"),
]

if BOT_DATABASE_EXPORT:
    admin_commands.append(BotCommand(command="db", description="📦 Получить БД"))


# Обновление списка команд в Telegram
async def set_commands(bot: Bot):
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    for admin in get_admins():
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin))
        except Exception:
            bot_logger.warning("Не удалось обновить команды для админа %s", admin, exc_info=True)
