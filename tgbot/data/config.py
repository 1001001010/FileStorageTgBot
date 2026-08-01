# - *- coding: utf- 8 - *-
from functools import lru_cache
from pathlib import Path
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pytz import UnknownTimeZoneError, timezone

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"


# Все настройки из окружения или локального .env
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    bot_token: str = Field(default="", validation_alias=AliasChoices("BOT_TOKEN", "bot_token"))
    admin_ids: List[int] = Field(default_factory=list, validation_alias=AliasChoices("BOT_ADMIN_IDS", "admin_id"))
    database_export: bool = Field(default=False,
                                  validation_alias=AliasChoices("BOT_DATABASE_EXPORT", "allow_database_export"))
    status_notification: bool = Field(default=True, validation_alias="BOT_STATUS_NOTIFICATION")
    timezone: str = Field(default="Europe/Moscow", validation_alias="BOT_TIMEZONE")
    database_path: str = Field(default="tgbot/data/database.db", validation_alias="PATH_DATABASE")
    logs_path: str = Field(default="tgbot/data/logs.log", validation_alias="PATH_LOGS")
    user_cache_ttl: int = Field(default=300, ge=0, validation_alias="BOT_USER_CACHE_TTL")
    throttle_rate: float = Field(default=0.5, ge=0, validation_alias="BOT_THROTTLE_RATE")

    @field_validator("bot_token", "timezone", "database_path", "logs_path", mode="before")
    @classmethod
    def _strip_string(cls, value: object) -> str:
        return str(value or "").strip()

    @field_validator("admin_ids", mode="before")
    @classmethod
    def _parse_admin_ids(cls, value: object) -> List[int]:
        if value is None or value == "":
            return []

        if isinstance(value, int):
            values = [value]
        elif isinstance(value, str):
            values = [admin_id for admin_id in value.replace(" ", "").split(",") if admin_id]
        elif isinstance(value, (list, tuple, set)):
            values = list(value)
        else:
            raise ValueError("BOT_ADMIN_IDS должен быть числом или списком чисел через запятую")

        admin_ids = []

        for admin_id in values:
            try:
                parsed_id = int(admin_id)
            except (TypeError, ValueError) as error:
                raise ValueError("BOT_ADMIN_IDS должен содержать только Telegram ID через запятую") from error

            if parsed_id <= 0:
                raise ValueError("BOT_ADMIN_IDS должен содержать Telegram ID больше нуля")

            admin_ids.append(parsed_id)

        return admin_ids

    @field_validator("timezone")
    @classmethod
    def _validate_timezone(cls, value: str) -> str:
        try:
            timezone(value)
        except UnknownTimeZoneError as error:
            raise ValueError("BOT_TIMEZONE должен быть корректной временной зоной, например Europe/Moscow") from error

        return value

    @field_validator("database_path", "logs_path")
    @classmethod
    def _validate_path(cls, value: str) -> str:
        if not value:
            raise ValueError("Путь к файлу не должен быть пустым")

        return value

    @property
    def admins(self) -> List[int]:
        return list(self.admin_ids)

    def resolve_path(self, path_value: str) -> Path:
        path = Path(path_value)

        if path.is_absolute():
            return path

        return BASE_DIR / path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# Константы чтобы не ломать старые импорты в шаблоне
BOT_TOKEN = settings.bot_token.replace(" ", "")
PATH_DATABASE = str(settings.resolve_path(settings.database_path))
PATH_LOGS = str(settings.resolve_path(settings.logs_path))
BOT_STATUS_NOTIFICATION = settings.status_notification
BOT_DATABASE_EXPORT = settings.database_export
BOT_TIMEZONE = settings.timezone
BOT_USER_CACHE_TTL = settings.user_cache_ttl
BOT_THROTTLE_RATE = settings.throttle_rate
BOT_SCHEDULER = AsyncIOScheduler(timezone=BOT_TIMEZONE)


# Получение администраторов бота
def get_admins() -> List[int]:
    return settings.admins


# Проверка настроек, которые нужны именно для запуска бота
def validate_bot_config() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("В .env не заполнен параметр BOT_TOKEN")
