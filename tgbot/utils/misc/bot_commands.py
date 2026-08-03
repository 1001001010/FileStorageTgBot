# - *- coding: utf- 8 - *-
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

# Команды для обычных пользователей
user_commands = [
    BotCommand(command="start", description="♻️ Перезапустить бота"),
    BotCommand(command="upload", description="📤 Загрузить файл"),
    BotCommand(command="files", description="📂 Мои файлы"),
    BotCommand(command="favorites", description="⭐ Избранное"),
    BotCommand(command="links", description="🔗 Общие ссылки"),
    BotCommand(command="search", description="🔍 Поиск"),
    BotCommand(command="storage", description="📊 Хранилище"),
    BotCommand(command="trash", description="🗑 Корзина"),
    BotCommand(command="settings", description="⚙️ Настройки"),
    BotCommand(command="help", description="❓ Помощь"),
]

# Команды для админов
# admin_commands = [
#     BotCommand(command="start", description="♻️ Перезапуск бота"),
#     BotCommand(command="menu", description="🌀 Получение клавиатуры"),
#     BotCommand(command="log", description="🖨 Получить логи"),
# ]

# if settings.database_export:
#     admin_commands.append(BotCommand(command="db", description="📦 Получить БД"))


# Обновление списка команд в Telegram
async def set_commands(bot: Bot):
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    # for admin in get_admins():
    #     try:
    #         await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin))
    #     except Exception:
    #         bot_logger.warning("Не удалось обновить команды для админа %s", admin, exc_info=True)
