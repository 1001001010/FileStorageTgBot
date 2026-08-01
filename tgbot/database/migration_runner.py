# - *- coding: utf- 8 - *-
import asyncio
from contextlib import AbstractAsyncContextManager
from pathlib import Path
from typing import Optional

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from tgbot.database.core import database_url

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = PROJECT_ROOT / "alembic.ini"
MIGRATIONS_DIR = PROJECT_ROOT / "migrations"


# Собираем конфиг Alembic так, чтобы команды работали из любой папки
def get_alembic_config(url: str = database_url) -> Config:
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("script_location", str(MIGRATIONS_DIR))
    config.set_main_option("sqlalchemy.url", url)

    return config


# Применяем все миграции до последней версии
async def run_migrations(engine: Optional[AsyncEngine] = None) -> None:
    if engine is None:
        config = get_alembic_config()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, command.upgrade, config, "head")
        return

    config = get_alembic_config(str(engine.url))

    async with engine_context(engine) as connection:
        await connection.run_sync(_upgrade_with_connection, config)


# Отдельная обертка нужна, чтобы IDE корректно видела async context manager
def engine_context(engine: AsyncEngine) -> AbstractAsyncContextManager[AsyncConnection]:
    return engine.begin()


# Alembic умеет работать с синхронным соединением внутри async-engine
def _upgrade_with_connection(connection, config: Config) -> None:
    config.attributes["connection"] = connection
    command.upgrade(config, "head")


# Ручной запуск миграций из консоли
async def _main() -> None:
    await run_migrations()
    print("Миграции базы данных применены")


if __name__ == "__main__":
    asyncio.run(_main())
