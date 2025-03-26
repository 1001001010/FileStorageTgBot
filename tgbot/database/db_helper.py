# - *- coding: utf- 8 - *-
import sqlite3

from tgbot.data.config import PATH_DATABASE
from tgbot.utils.const_functions import ded


# Преобразование полученного списка в словарь
def dict_factory(cursor, row) -> dict:
    save_dict = {}

    for idx, col in enumerate(cursor.description):
        save_dict[col[0]] = row[idx]

    return save_dict


# Форматирование запроса без аргументов
def update_format(sql, parameters: dict) -> tuple[str, list]:
    values = ", ".join([ 
        f"{item} = ?" for item in parameters
    ])
    sql += f" {values}"

    return sql, list(parameters.values())


# Форматирование запроса с аргументами
def update_format_where(sql, parameters: dict) -> tuple[str, list]:
    sql += " WHERE "

    sql += " AND ".join([ 
        f"{item} = ?" for item in parameters
    ])

    return sql, list(parameters.values())


################################################################################
# Создание всех таблиц для БД
def create_dbx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory

        ############################################################
        # Создание таблицы с хранением - пользователей
        if len(con.execute("PRAGMA table_info(Users)").fetchall()) == 7:
            print("База данных найдена (1/5) - Таблица пользователей")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE Users(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        user_login TEXT,
                        user_name TEXT,
                        user_surname TEXT,
                        user_fullname TEXT,
                        created_at INTEGER NOT NULL
                    )
                """)
            )
            print("База данных не найдена (1/5) | Создаём таблицу пользователей...")

        # Создание таблицы для хранения папок
        if len(con.execute("PRAGMA table_info(Folders)").fetchall()) == 5:
            print("База данных найдена (2/5) - Таблица папок")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE Folders(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        folder_id INTEGER,
                        user_id INTEGER NOT NULL,
                        created_at INTEGER NOT NULL,
                        FOREIGN KEY (folder_id) REFERENCES Folders(id) ON DELETE CASCADE
                    )
                """)
            )
            print("База данных не найдена (3/5) | Создаём таблицу папок...")

        # Создание таблицы для хранения файлов
        if len(con.execute("PRAGMA table_info(Files)").fetchall()) == 11:
            print("База данных найдена (3/5) - Таблица файлов")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE Files(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        path TEXT NOT NULL,
                        user_id INTEGER NOT NULL,
                        folder_id INTEGER,
                        extensions_id INTEGER,
                        mime_type_id INTEGER,
                        file_hash TEXT NOT NULL,
                        size INTEGER NOT NULL,
                        created_at INTEGER NOT NULL,
                        views INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
                        FOREIGN KEY (folder_id) REFERENCES Folders(id) ON DELETE CASCADE,
                        FOREIGN KEY (extensions_id) REFERENCES Extensions(id) ON DELETE CASCADE,
                        FOREIGN KEY (mime_type_id) REFERENCES MimeTypes(id) ON DELETE CASCADE
                    )
                """)
            )
            print("База данных не найдена (3/5) | Создаём таблицу файлов...")

        # Создание таблицы для хранения расширений
        if len(con.execute("PRAGMA table_info(Extensions)").fetchall()) == 3:
            print("База данных найдена (4/5) - Таблица расширений")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE Extensions(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        extension TEXT NOT NULL,
                        created_at INTEGER NOT NULL
                    )
                """)
            )
            print("База данных не найдена (4/5) | Создаём таблицу расширений...")

        # Создание таблицы для хранения MIME-типов
        if len(con.execute("PRAGMA table_info(MimeTypes)").fetchall()) == 3:
            print("База данных найдена (5/5) - Таблица MIME-типов")
        else:
            con.execute(
                ded(f"""
                    CREATE TABLE MimeTypes(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mime_type TEXT NOT NULL,
                        created_at INTEGER NOT NULL
                    )
                """)
            )
            print("База данных не найдена (5/5) | Создаём таблицу MIME-типов...")
