# - *- coding: utf- 8 - *-
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.handlers import ErrorHandler

from tgbot.utils.misc.bot_logging import bot_logger

router = Router(name=__name__)


# Ошибка при отправке сообщения пользователю, который заблокировал бота
# @router.errors(ExceptionTypeFilter(TelegramForbiddenError))
# class ForbiddenErrorHandler(ErrorHandler):
#     async def handle(self):
#         ...


# Безопасно игнорируем повторное редактирование сообщения без изменений
@router.errors(ExceptionTypeFilter(TelegramBadRequest))
class MessageNotModifiedHandler(ErrorHandler):
    async def handle(self):
        if "message is not modified" in self.exception_message.lower():
            bot_logger.debug("Telegram отклонил повторное редактирование сообщения без изменений")
            return True

        raise self.event
