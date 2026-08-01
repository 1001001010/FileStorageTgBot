# - *- coding: utf- 8 - *-
from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from tgbot.data.config import get_admins


# Проверка, что действия совершает админ
class IsAdmin(BaseFilter):
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        user = getattr(event, "from_user", None)

        return bool(user and user.id in get_admins())


# Проверка приватного чата
class IsPrivate(BaseFilter):
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        chat = getattr(event, "chat", None)
        message = getattr(event, "message", None)

        if chat is None and message is not None:
            chat = message.chat

        if chat is None:
            return True

        return chat.type == "private"
