# - *- coding: utf- 8 - *-
import sqlite3

from pydantic import BaseModel

from tgbot.data.config import PATH_DATABASE
from tgbot.database.db_helper import dict_factory, update_format_where, update_format
from tgbot.utils.const_functions import get_unix, ded


# Модель таблицы
class UserModel(BaseModel):
    id: int  # Инкремент записи
    user_id: int  # Айди пользователя
    user_login: str  # Юзернейм пользователя
    user_name: str  # Имя пользователя
    user_surname: str  # Фамилия пользователя
    user_fullname: str  # Полное имя + фамилия пользователя
    created_at: int  # Дата регистрации пользователя в боте (в UNIX времени)


class Userx:
    storage_name = "Users"

    # Добавление записи
    @staticmethod
    def add(
            user_id: int,
            user_login: str,
            user_name: str,
            user_surname: str,
            user_fullname: str,
    ):
        created_at = get_unix()

        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory

            con.execute(
                ded(f"""
                    INSERT INTO {Userx.storage_name} (
                        user_id,
                        user_login,
                        user_name,
                        user_surname,
                        user_fullname,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """),
                [
                    user_id,
                    user_login,
                    user_name,
                    user_surname,
                    user_fullname,
                    created_at,
                ],
            )

    # Получение записи
    @staticmethod
    def get(**kwargs) -> UserModel:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Userx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            response = con.execute(sql, parameters).fetchone()

            if response is not None:
                response = UserModel(**response)

            return response

    # Получение записей
    @staticmethod
    def gets(**kwargs) -> list[UserModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Userx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            response = con.execute(sql, parameters).fetchall()

            if len(response) >= 1:
                response = [UserModel(**cache_object) for cache_object in response]

            return response

    # Получение всех записей
    @staticmethod
    def get_all() -> list[UserModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"SELECT * FROM {Userx.storage_name}"

            response = con.execute(sql).fetchall()

            if len(response) >= 1:
                response = [UserModel(**cache_object) for cache_object in response]

            return response

    # Редактирование записи
    @staticmethod
    def update(user_id, **kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"UPDATE {Userx.storage_name} SET"
            sql, parameters = update_format(sql, kwargs)
            parameters.append(user_id)

            con.execute(sql + "WHERE user_id = ?", parameters)

    # Удаление записи
    @staticmethod
    def delete(**kwargs):
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Userx.storage_name}"
            sql, parameters = update_format_where(sql, kwargs)

            con.execute(sql, parameters)

    # Получение пользователей за определенный период
    @staticmethod
    def get_by_period(start_time: int) -> list[UserModel]:
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"""
                SELECT * FROM {Userx.storage_name}
                WHERE created_at >= ?
            """
            response = con.execute(sql, (start_time,)).fetchall()

            return [UserModel(**user) for user in response] if response else []

    # Очистка всех записей
    @staticmethod
    def clear():
        with sqlite3.connect(PATH_DATABASE) as con:
            con.row_factory = dict_factory
            sql = f"DELETE FROM {Userx.storage_name}"

            con.execute(sql)