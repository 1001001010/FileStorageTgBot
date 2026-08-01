# - *- coding: utf- 8 - *-
from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from pathlib import Path

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from tgbot.data.config import PATH_DATABASE

database_path = Path(PATH_DATABASE)
database_url = f"sqlite+aiosqlite:///{database_path.as_posix()}"

engine = create_async_engine(database_url, echo=False)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


# Общая база для всех SQLAlchemy-моделей
class Base(AsyncAttrs, DeclarativeBase):
    pass


# SQLite по умолчанию не включает foreign keys, поэтому включаем явно
@event.listens_for(engine.sync_engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Открываем сессию и сами отвечаем за сохранение или откат
@asynccontextmanager
async def _session_scope() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Отдельная обертка, чтобы IDE нормально видела асинхронный контекст
def session_scope() -> AbstractAsyncContextManager[AsyncSession]:
    return _session_scope()


# Закрываем пул соединений при остановке приложения
async def close_database() -> None:
    await engine.dispose()
