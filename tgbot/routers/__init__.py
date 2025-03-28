# - *- coding: utf- 8 - *-
from aiogram import Dispatcher, F

from tgbot.routers import main_errors, main_missed, main_start
from tgbot.routers.admin import admin_menu
from tgbot.routers.user import user_menu, user_folder, user_file, folder_and_files
from tgbot.utils.misc.bot_filters import IsAdmin


# Регистрация всех роутеров
def register_all_routers(dp: Dispatcher):
    # Подключение фильтров
    main_errors.router.message.filter(F.chat.type == "private")
    main_start.router.message.filter(F.chat.type == "private")

    user_menu.router.message.filter(F.chat.type == "private")
    user_folder.router.message.filter(F.chat.type == "private")
    user_file.router.message.filter(F.chat.type == "private")
    folder_and_files.router.message.filter(F.chat.type == "private")
    admin_menu.router.message.filter(F.chat.type == "private", IsAdmin())

    main_missed.router.message.filter(F.chat.type == "private")

    # Подключение обязательных роутеров
    dp.include_router(main_errors.router)  # Роутер ошибки
    dp.include_router(main_start.router)  # Роутер основных команд

    # Подключение пользовательских роутеров (юзеров и админов)
    # Роуты пользователей
    dp.include_router(user_menu.router)
    dp.include_router(user_folder.router)
    dp.include_router(user_file.router)
    dp.include_router(folder_and_files.router)
    
    # Роуты админов
    dp.include_router(admin_menu.router)

    # Подключение обязательных роутеров
    dp.include_router(main_missed.router)  # Роутер пропущенных апдейтов