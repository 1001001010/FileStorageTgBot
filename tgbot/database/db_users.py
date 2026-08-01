# - *- coding: utf- 8 - *-
from sqlalchemy import BigInteger, Integer, String, or_
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Mapped, mapped_column

from tgbot.database.core import Base, session_scope
from tgbot.database.repository import BaseRepository
from tgbot.utils.const_functions import get_unix


# Модель пользователя Telegram
class UserModel(Base):
    __tablename__ = "storage_users"

    increment: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True, index=True)
    user_login: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    user_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    user_surname: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    user_fullname: Mapped[str] = mapped_column(String(511), nullable=False, default="")
    user_unix: Mapped[int] = mapped_column(Integer, nullable=False, default=get_unix)


ModelBase = UserModel
BaseModel = UserModel


# Репозиторий пользователей
class UsersRepository(BaseRepository[UserModel]):
    def __init__(self):
        super().__init__()
        self.table_model = UserModel
        self.storage_name = UserModel.__tablename__

    # Для совместимости add ведет себя как upsert
    async def add(
            self,
            user_id: int,
            user_login: str,
            user_name: str,
            user_surname: str,
            user_fullname: str,
    ) -> UserModel:
        return await self.upsert(
            user_id=user_id,
            user_login=user_login,
            user_name=user_name,
            user_surname=user_surname,
            user_fullname=user_fullname,
        )

    # Создание пользователя или обновление его данных по user_id
    async def upsert(
            self,
            user_id: int,
            user_login: str,
            user_name: str,
            user_surname: str,
            user_fullname: str,
    ) -> UserModel:
        statement = insert(UserModel).values(
            user_id=user_id,
            user_login=user_login,
            user_name=user_name,
            user_surname=user_surname,
            user_fullname=user_fullname,
            user_unix=get_unix(),
        )
        statement = statement.on_conflict_do_update(
            index_elements=[UserModel.user_id],
            set_={
                "user_login": statement.excluded.user_login,
                "user_name": statement.excluded.user_name,
                "user_surname": statement.excluded.user_surname,
                "user_fullname": statement.excluded.user_fullname,
            },
            where=or_(
                UserModel.user_login != statement.excluded.user_login,
                UserModel.user_name != statement.excluded.user_name,
                UserModel.user_surname != statement.excluded.user_surname,
                UserModel.user_fullname != statement.excluded.user_fullname,
            ),
        )

        async with session_scope() as session:
            await session.execute(statement)

        user = await self.get(user_id=user_id)

        if user is None:
            raise RuntimeError("Пользователь не сохранился")

        return user

    # Обновление пользователя по Telegram ID
    async def update(self, user_id: int, **kwargs) -> None:
        if not kwargs:
            return

        async with session_scope() as session:
            await session.execute(
                sqlalchemy_update(UserModel)
                .where(UserModel.user_id == user_id)
                .values(**kwargs)
            )
