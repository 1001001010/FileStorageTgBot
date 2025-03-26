import sqlite3
from pydantic import BaseModel

from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format_where, update_format
from tgbot.utils.const_functions import get_unix, ded

# Модель таблицы
class FolderModel(BaseModel):
    id: int  # Инкремент записи
    name: str  # Имя папки
    folder_id: int # ID родительской папки
    user_id: int  # ID пользователя, создавшего папку
    created_at: int  # Дата создания в UNIX-времени

class Folderx:
    storage_name = "Folders"

    # Добавление записи
    @staticmethod
    def add(
            name: str,
            user_id: int,
            folder_id: int,
    ):
        created_at = get_unix()
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            con.execute(
                ded(f"""
                    INSERT INTO {Folderx.storage_name} (
                        name, folder_id, user_id, created_at
                    ) VALUES (?, ?, ?, ?)
                """),
                [name, folder_id, user_id, created_at]
            )

    # Получение записи
    @staticmethod
    def get(**kwargs) -> FolderModel:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Folderx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            response = con.execute(sql, parameters).fetchone()

            if response is not None:
                response = FolderModel(**response)

            return response

    # Получение записей
    @staticmethod
    def gets(**kwargs) -> list[FolderModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Folderx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            response = con.execute(sql, parameters).fetchall()

            if len(response) >= 1:
                response = [FolderModel(**cache_object) for cache_object in response]

            return response

    # Получение всех записей
    @staticmethod
    def get_all() -> list[FolderModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Folderx.storage_name}"
            response = con.execute(sql).fetchall()

            if len(response) >= 1:
                response = [FolderModel(**cache_object) for cache_object in response]
                
            return response

    # Редактирование записи
    @staticmethod
    def update(folder_id, **kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"UPDATE {Folderx.storage_name} SET"
            sql, parameters = update_format(sql, kwargs)
            parameters.append(folder_id)
            con.execute(sql + " WHERE id = ?", parameters)

    # Удаление записи
    @staticmethod
    def delete(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Folderx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)
            con.execute(sql, parameters)

    # Очистка всех записей
    @staticmethod
    def clear():
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Folderx.storage_name}"
            con.execute(sql)
