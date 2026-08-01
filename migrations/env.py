# - *- coding: utf- 8 - *-
import asyncio
from contextlib import AbstractAsyncContextManager
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, async_engine_from_config

from tgbot.database.core import Base

# Импортируем модели, чтобы Alembic видел все таблицы
import tgbot.database  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# Настройка миграций без подключения к базе
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# Настройка миграций поверх готового соединения
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# Создаем async-engine и передаем Alembic синхронное соединение внутри run_sync
async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable_context(connectable) as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# Отдельная обертка помогает IDE правильно определить async context manager
def connectable_context(connectable: AsyncEngine) -> AbstractAsyncContextManager[AsyncConnection]:
    return connectable.connect()


if context.is_offline_mode():
    run_migrations_offline()
else:
    external_connection = config.attributes.get("connection")

    if external_connection is not None:
        do_run_migrations(external_connection)
    else:
        asyncio.run(run_async_migrations())
