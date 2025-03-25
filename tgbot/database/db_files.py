import sqlite3
from pydantic import BaseModel

from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format_where, update_format
from tgbot.utils.const_functions import get_unix, ded

# Модель таблицы
class FileModel(BaseModel):
    id: int  # Инкремент записи
    name: str  # Имя файла
    path: str  # Путь к файлу
    extensions_id: int  # ID расширения
    mime_type: str  # MIME-тип файла
    file_hash: str  # Хеш файла
    user_id: int  # ID пользователя, загрузившего файл
    size: int  # Размер файла в байтах
    created_at: int  # Дата создания файла в UNIX-времени

# Работа с файлами
class Filex:
    storage_name = "Files"

    # Добавление записи
    @staticmethod
    def add(
            name: str,
            path: str,
            extensions_id: int,
            mime_type: str,
            file_hash: str,
            user_id: int,
            size: int,
    ):
        created_at = get_unix()

        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            con.execute(
                ded(f"""
                    INSERT INTO {Filex.storage_name} (
                        name, path, extensions_id, mime_type, file_hash, user_id, size, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """),
                [name, path, extensions_id, mime_type, file_hash, user_id, size, created_at]
            )

    # Получение записи
    @staticmethod
    def get(**kwargs) -> FileModel:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Filex.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)
            response = con.execute(sql, parameters).fetchone()

            return FileModel(**response) if response else None

    # Получение записей
    @staticmethod
    def gets(**kwargs) -> list[FileModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Filex.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)
            response = con.execute(sql, parameters).fetchall()

            return [FileModel(**cache_object) for cache_object in response] if response else []

    # Получение всех записей
    @staticmethod
    def get_all() -> list[FileModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Filex.storage_name}"
            response = con.execute(sql).fetchall()

            return [FileModel(**cache_object) for cache_object in response] if response else []

    # Редактирование записи
    @staticmethod
    def update(file_id, **kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"UPDATE {Filex.storage_name} SET"
            sql, parameters = update_format(sql, kwargs)
            parameters.append(file_id)
            con.execute(sql + " WHERE id = ?", parameters)

    # Удаление записи
    @staticmethod
    def delete(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Filex.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)
            con.execute(sql, parameters)

    # Очистка всех записей
    @staticmethod
    def clear():
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Filex.storage_name}"
            con.execute(sql)
