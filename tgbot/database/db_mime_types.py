from pydantic import BaseModel
import sqlite3
from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format_where, update_format
from tgbot.utils.const_functions import get_unix, ded

# Модель таблицы
class MimeTypeModel(BaseModel):
    id: int  # Инкремент записи
    mime_type: str  # MIME-тип
    created_at: int  # Дата создания записи в UNIX-времени

class MimeTypesx:
    storage_name = "MimeTypes"

    # Добавление записи
    @staticmethod
    def add(mime_type: str):
        created_at = get_unix()

        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            con.execute(
                ded(f"""
                    INSERT INTO {MimeTypesx.storage_name} (
                        mime_type, created_at
                    ) VALUES (?, ?)
                """),
                [mime_type, created_at]
            )

    # Получение записи
    @staticmethod
    def get(**kwargs) -> MimeTypeModel:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {MimeTypesx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)
            response = con.execute(sql, parameters).fetchone()

            return MimeTypeModel(**response) if response else None

    # Получение записей
    @staticmethod
    def gets(**kwargs) -> list[MimeTypeModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {MimeTypesx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)
            response = con.execute(sql, parameters).fetchall()

            return [MimeTypeModel(**cache_object) for cache_object in response] if response else []

    # Получение всех записей
    @staticmethod
    def get_all() -> list[MimeTypeModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {MimeTypesx.storage_name}"
            response = con.execute(sql).fetchall()

            return [MimeTypeModel(**cache_object) for cache_object in response] if response else []

    # Редактирование записи
    @staticmethod
    def update(mime_type_id, **kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"UPDATE {MimeTypesx.storage_name} SET"
            sql, parameters = update_format(sql, kwargs)
            parameters.append(mime_type_id)
            con.execute(sql + " WHERE id = ?", parameters)

    # Удаление записи
    @staticmethod
    def delete(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {MimeTypesx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)
            con.execute(sql, parameters)

    # Очистка всех записей
    @staticmethod
    def clear():
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {MimeTypesx.storage_name}"
            con.execute(sql)