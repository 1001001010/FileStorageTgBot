# - *- coding: utf- 8 - *-
from aiogram import Dispatcher

from tgbot.routers import main_errors, main_missed, main_start
from tgbot.routers.admin import admin_menu
from tgbot.routers.user import user_menu
from tgbot.utils.misc.bot_filters import IsAdmin, IsPrivate


# Подключение всех роутеров
def register_all_routers(dp: Dispatcher):
    # Общие фильтры для приватных чатов
    main_errors.router.message.filter(IsPrivate())
    main_start.router.message.filter(IsPrivate())

    user_menu.router.message.filter(IsPrivate())
    user_menu.router.callback_query.filter(IsPrivate())
    admin_menu.router.message.filter(IsPrivate(), IsAdmin())
    admin_menu.router.callback_query.filter(IsPrivate(), IsAdmin())

    main_missed.router.message.filter(IsPrivate())
    main_missed.router.callback_query.filter(IsPrivate())

    # Базовые роутеры, которые нужны всегда
    dp.include_router(main_errors.router)  # Ошибки
    dp.include_router(main_start.router)  # Старт и главное меню

    # Роутеры для пользователей и админов
    dp.include_router(user_menu.router)  # Пользовательские обработчики
    dp.include_router(admin_menu.router)  # Админские обработчики

    # Обработка всего, что не поймали выше
    dp.include_router(main_missed.router)  # Пропущенные сообщения и колбэки
