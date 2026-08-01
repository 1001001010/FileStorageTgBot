# - *- coding: utf- 8 - *-
from aiogram import Dispatcher

from tgbot.middlewares.middleware_throttling import ThrottlingMiddleware
from tgbot.middlewares.middleware_user import ExistsUserMiddleware


# Подключение всех мидлварей
def register_all_middlewares(dp: Dispatcher):
    dp.callback_query.outer_middleware(ExistsUserMiddleware())
    dp.message.outer_middleware(ExistsUserMiddleware())

    throttling = ThrottlingMiddleware()
    dp.message.middleware(throttling)
    dp.callback_query.middleware(throttling)


# Старое имя оставлено, чтобы не ломать импорт в чужих проектах на базе шаблона
def register_all_middlwares(dp: Dispatcher):
    register_all_middlewares(dp)
