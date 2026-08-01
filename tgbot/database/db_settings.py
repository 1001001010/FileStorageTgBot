# - *- coding: utf- 8 - *-
from sqlalchemy import Boolean, Integer
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Mapped, mapped_column

from tgbot.database.core import Base, session_scope
from tgbot.database.repository import BaseRepository


# Модель настроек бота
class SettingsModel(Base):
    __tablename__ = "storage_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    status_work: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


ModelBase = SettingsModel
BaseModel = SettingsModel


# Репозиторий настроек бота
class SettingsRepository(BaseRepository[SettingsModel]):
    def __init__(self):
        super().__init__()
        self.table_model = SettingsModel
        self.storage_name = SettingsModel.__tablename__

    # Создание строки настроек если их еще нет
    async def ensure_default(self) -> None:
        statement = insert(SettingsModel).values(id=1, status_work=False)
        statement = statement.on_conflict_do_nothing(index_elements=[SettingsModel.id])

        async with session_scope() as session:
            await session.execute(statement)

    # Настройки должны быть всегда, поэтому при пустой таблице создаем дефолт
    async def get(self) -> SettingsModel:
        settings = await super().get(id=1)

        if settings is None:
            await self.ensure_default()
            settings = await super().get(id=1)

        if settings is None:
            raise RuntimeError("Настройки бота по умолчанию не сохранились")

        return settings

    # Обновление единственной строки настроек
    async def update(self, **kwargs) -> None:
        if not kwargs:
            return

        async with session_scope() as session:
            await session.execute(
                sqlalchemy_update(SettingsModel)
                .where(SettingsModel.id == 1)
                .values(**kwargs)
            )
