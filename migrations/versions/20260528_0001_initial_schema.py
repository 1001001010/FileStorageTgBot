"""Начальная схема проекта

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-28 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Проверяем таблицу через sqlite_master, потому что первая миграция должна принять и старую БД
def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = :table_name
            """
        ),
        {"table_name": table_name},
    )

    return result.scalar_one_or_none() is not None


# Проверяем колонку перед миграцией старой таблицы
def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(sa.text(f"PRAGMA table_info({table_name})"))

    return column_name in [row.name for row in result]


def upgrade() -> None:
    bind = op.get_bind()

    if _table_exists("storage_users"):
        bind.execute(sa.text("DELETE FROM storage_users WHERE user_id IS NULL"))
        bind.execute(
            sa.text(
                """
                DELETE
                FROM storage_users
                WHERE user_id IS NOT NULL
                  AND rowid NOT IN (SELECT MAX(rowid) AS last_rowid
                                    FROM storage_users
                                    WHERE user_id IS NOT NULL
                                    GROUP BY user_id)
                """
            )
        )
    else:
        op.create_table(
            "storage_users",
            sa.Column("increment", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.BigInteger(), nullable=False),
            sa.Column("user_login", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("user_name", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("user_surname", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("user_fullname", sa.String(length=511), nullable=False, server_default=""),
            sa.Column("user_unix", sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint("increment"),
        )

    op.create_index("ix_storage_users_user_id", "storage_users", ["user_id"], unique=True, if_not_exists=True)

    if _table_exists("storage_settings"):
        status_source = "status_work" if _column_exists("storage_settings", "status_work") else "'false'"
        bind.execute(sa.text("DROP TABLE IF EXISTS storage_settings_new"))
        bind.execute(
            sa.text(
                """
                CREATE TABLE storage_settings_new
                (
                    id          INTEGER NOT NULL PRIMARY KEY,
                    status_work BOOLEAN NOT NULL DEFAULT 0
                )
                """
            )
        )
        bind.execute(
            sa.text(
                """
                INSERT INTO storage_settings_new (id, status_work)
                SELECT 1 AS id,
                       CASE LOWER(CAST(COALESCE({status_source}, 'false') AS TEXT))
                           WHEN '1' THEN 1
                           WHEN 'true' THEN 1
                           WHEN 'yes' THEN 1
                           WHEN 'on' THEN 1
                           WHEN 'да' THEN 1
                           ELSE 0
                       END AS status_work
                FROM storage_settings
                LIMIT 1
                """
                .format(status_source=status_source)
            )
        )
        bind.execute(sa.text("DROP TABLE storage_settings"))
        bind.execute(sa.text("ALTER TABLE storage_settings_new RENAME TO storage_settings"))
    else:
        op.create_table(
            "storage_settings",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("status_work", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.PrimaryKeyConstraint("id"),
        )

    bind.execute(
        sa.text(
            """
            INSERT INTO storage_settings (id, status_work)
            SELECT 1 AS id, 0 AS status_work
            WHERE NOT EXISTS (SELECT 1 AS exists_status FROM storage_settings WHERE id = 1)
            """
        )
    )


def downgrade() -> None:
    op.drop_table("storage_settings")
    op.drop_index("ix_storage_users_user_id", table_name="storage_users")
    op.drop_table("storage_users")
