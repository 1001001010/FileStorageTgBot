# - *- coding: utf- 8 - *-
from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import select
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.exc import SQLAlchemyError

from tgbot.database.core import Base, database_path, session_scope
from tgbot.utils.misc.bot_logging import bot_logger

ModelTranslator = TypeVar("ModelTranslator", bound=Base)


# Базовый репозиторий с общими методами работы с БД
class BaseRepository(Generic[ModelTranslator]):
    def __init__(self):
        self.storage_name = "storage"
        self.table_model: Optional[Type[ModelTranslator]] = None

    # Без модели репозиторий работать не должен
    def _model(self) -> Type[ModelTranslator]:
        if self.table_model is None:
            raise RuntimeError("Модель базы данных не настроена")

        return self.table_model

    # Удаление только по явному фильтру, без случайной чистки всей таблицы
    async def delete(self, **kwargs) -> None:
        if not kwargs:
            raise ValueError("Для удаления нужен хотя бы один фильтр")

        model = self._model()

        async with session_scope() as session:
            await session.execute(sqlalchemy_delete(model).filter_by(**kwargs))

    # Полное удаление всех строк таблицы. Название намеренно прямое.
    async def delete_all_rows(self) -> None:
        model = self._model()

        async with session_scope() as session:
            await session.execute(sqlalchemy_delete(model))

    # Возвращение первой записи по фильтру
    async def get(self, **kwargs) -> Optional[ModelTranslator]:
        model = self._model()
        statement = select(model).filter_by(**kwargs)

        async with session_scope() as session:
            response = await session.execute(statement)

            return response.scalars().first()

    # Возвращение всех записей по фильтру
    async def gets(self, **kwargs) -> List[ModelTranslator]:
        model = self._model()
        statement = select(model).filter_by(**kwargs)

        async with session_scope() as session:
            response = await session.execute(statement)

            return list(response.scalars().all())

    # Возвращение всей таблицы
    async def get_all(self) -> List[ModelTranslator]:
        model = self._model()

        async with session_scope() as session:
            response = await session.execute(select(model))

            return list(response.scalars().all())

    # Обновляем только записи, которые попали под фильтр
    async def update(self, filters: dict, **kwargs) -> None:
        if not filters:
            raise ValueError("Для обновления нужен хотя бы один фильтр")

        if not kwargs:
            return

        model = self._model()

        async with session_scope() as session:
            await session.execute(
                sqlalchemy_update(model)
                .filter_by(**filters)
                .values(**kwargs)
            )


# Готовим подключение к БД. Сами миграции запускаются отдельно через migrate.py.
async def prepare_database() -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)

    # Импортируем модели, чтобы репозитории работали с уже загруженными таблицами
    import tgbot.database  # noqa: F401

    from tgbot.database.db_settings import SettingsRepository

    try:
        await SettingsRepository().ensure_default()
    except SQLAlchemyError as error:
        raise RuntimeError("База данных не готова. Запусти миграции командой: python migrate.py") from error

    bot_logger.info("База данных готова")
