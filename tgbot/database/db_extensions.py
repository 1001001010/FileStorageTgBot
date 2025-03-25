from pydantic import BaseModel
import sqlite3
from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format_where, update_format
from tgbot.utils.const_functions import get_unix, ded

# Модель таблицы
class ExtensionModel(BaseModel):
    id: int  # Инкремент записи
    extension: str  # Расширение файла
    created_at: int  # Дата создания записи в UNIX-времени

# Работа с расширениями
class Extensionsx:
    storage_name = "Extensions"

    # Добавление записи
    @staticmethod
    def add(extension: str):
        created_at = get_unix()

        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            con.execute(
                ded(f"""
                    INSERT INTO {Extensionsx.storage_name} (
                        extension, created_at
                    ) VALUES (?, ?)
                """),
                [extension, created_at]
            )

    # Получение записи
    @staticmethod
    def get(**kwargs) -> ExtensionModel:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Extensionsx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)
            response = con.execute(sql, parameters).fetchone()

            return ExtensionModel(**response) if response else None

    # Получение записей
    @staticmethod
    def gets(**kwargs) -> list[ExtensionModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Extensionsx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)
            response = con.execute(sql, parameters).fetchall()

            return [ExtensionModel(**cache_object) for cache_object in response] if response else []

    # Получение всех записей
    @staticmethod
    def get_all() -> list[ExtensionModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Extensionsx.storage_name}"
            response = con.execute(sql).fetchall()

            return [ExtensionModel(**cache_object) for cache_object in response] if response else []

    # Редактирование записи
    @staticmethod
    def update(extension_id, **kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"UPDATE {Extensionsx.storage_name} SET"
            sql, parameters = update_format(sql, kwargs)
            parameters.append(extension_id)
            con.execute(sql + " WHERE id = ?", parameters)

    # Удаление записи
    @staticmethod
    def delete(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Extensionsx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)
            con.execute(sql, parameters)

    # Очистка всех записей
    @staticmethod
    def clear():
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Extensionsx.storage_name}"
            con.execute(sql)