# - *- coding: utf- 8 - *-
import argparse
from typing import Optional

from alembic import command
from alembic.config import Config

HELP_TEXT = """
Миграции базы данных

Безопасное правило:
  python migrate.py                 только показывает эту справку
  действия с БД выполняются только при явной команде

Основные команды:
  python migrate.py help                 показать эту справку
  python migrate.py up                   применить все миграции до head
  python migrate.py down                 откатить последнюю миграцию
  python migrate.py new "add users"      создать пустую миграцию
  python migrate.py auto "add users"     создать миграцию по SQLAlchemy-моделям
  python migrate.py status               показать текущую версию и последние версии

Длинные команды:
  python migrate.py upgrade [rev]        применить миграции до rev, по умолчанию head
  python migrate.py downgrade [rev]      откатить миграции до rev, по умолчанию -1
  python migrate.py revision -m "name"   создать пустую миграцию
  python migrate.py current              показать текущую версию БД
  python migrate.py history              показать историю миграций
  python migrate.py heads                показать последние версии веток

Короткие алиасы:
  up       -> upgrade
  down     -> downgrade
  new      -> revision
  auto     -> revision --autogenerate
  autogen  -> auto
  cur      -> current
  hist     -> history
  st       -> status

Подсказки:
  - сначала меняешь SQLAlchemy-модель;
  - потом запускаешь: python migrate.py auto "что изменилось";
  - проверяешь файл в migrations/versions/;
  - применяешь: python migrate.py up;
  - если сомневаешься, запускаешь: python migrate.py status.
""".strip()


# Создаем parser без лишнего шума, чтобы help был похож на нормальную подсказку
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Удобный CLI для Alembic-миграций",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=True,
    )
    subparsers = parser.add_subparsers(dest="command")

    help_parser = subparsers.add_parser("help", aliases=["h"], help="Показать понятную справку")
    help_parser.set_defaults(action=show_help)

    upgrade_parser = subparsers.add_parser("upgrade", aliases=["up"], help="Применить миграции")
    upgrade_parser.add_argument("revision", nargs="?", default="head", help="Версия миграции, по умолчанию head")
    upgrade_parser.set_defaults(action=run_upgrade)

    downgrade_parser = subparsers.add_parser("downgrade", aliases=["down"], help="Откатить миграции")
    downgrade_parser.add_argument("revision", nargs="?", default="-1", help="Версия отката, по умолчанию -1")
    downgrade_parser.set_defaults(action=run_downgrade)

    revision_parser = subparsers.add_parser("revision", aliases=["new"], help="Создать пустую миграцию")
    revision_parser.add_argument("message", nargs="?", help="Название миграции")
    revision_parser.add_argument("-m", "--message-option", dest="message_option", help="Название миграции")
    revision_parser.add_argument("--autogenerate", "-a", action="store_true", help="Собрать изменения из моделей")
    revision_parser.set_defaults(action=run_revision)

    auto_parser = subparsers.add_parser("auto", aliases=["autogen"], help="Создать миграцию по моделям")
    auto_parser.add_argument("message", nargs="?", help="Название миграции")
    auto_parser.add_argument("-m", "--message-option", dest="message_option", help="Название миграции")
    auto_parser.set_defaults(action=run_auto_revision)

    current_parser = subparsers.add_parser("current", aliases=["cur"], help="Показать текущую версию БД")
    current_parser.set_defaults(action=run_current)

    history_parser = subparsers.add_parser("history", aliases=["hist"], help="Показать историю миграций")
    history_parser.set_defaults(action=run_history)

    heads_parser = subparsers.add_parser("heads", help="Показать последние версии веток")
    heads_parser.set_defaults(action=run_heads)

    status_parser = subparsers.add_parser("status", aliases=["st"], help="Показать текущую версию и heads")
    status_parser.set_defaults(action=run_status)

    return parser


def show_help(_config: Optional[Config], _args: argparse.Namespace) -> None:
    print(HELP_TEXT)


def run_upgrade(config: Config, args: argparse.Namespace) -> None:
    print(f"Применяю миграции до версии: {args.revision}")
    command.upgrade(config, args.revision)
    print("Готово")


def run_downgrade(config: Config, args: argparse.Namespace) -> None:
    print(f"Откатываю миграции до версии: {args.revision}")
    command.downgrade(config, args.revision)
    print("Готово")


def run_revision(config: Config, args: argparse.Namespace) -> None:
    message = get_revision_message(args)
    print(f"Создаю миграцию: {message}")
    command.revision(config, message=message, autogenerate=args.autogenerate)
    print("Готово")


def run_auto_revision(config: Config, args: argparse.Namespace) -> None:
    message = get_revision_message(args)
    print(f"Создаю миграцию по моделям: {message}")
    command.revision(config, message=message, autogenerate=True)
    print("Готово")


def run_current(config: Config, _args: argparse.Namespace) -> None:
    print("Текущая версия БД:")
    command.current(config)


def run_history(config: Config, _args: argparse.Namespace) -> None:
    print("История миграций:")
    command.history(config)


def run_heads(config: Config, _args: argparse.Namespace) -> None:
    print("Последние версии миграций:")
    command.heads(config)


def run_status(config: Config, args: argparse.Namespace) -> None:
    run_current(config, args)
    print()
    run_heads(config, args)


def get_revision_message(args: argparse.Namespace) -> str:
    message: Optional[str] = args.message_option or args.message

    if not message:
        raise SystemExit("Укажи название миграции. Пример: python migrate.py auto \"add users\"")

    return message


def get_config() -> Config:
    from tgbot.database.migration_runner import get_alembic_config

    return get_alembic_config()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        show_help(None, args)
        return

    if args.action == show_help:
        show_help(None, args)
        return

    if args.action in (run_revision, run_auto_revision):
        get_revision_message(args)

    config = get_config()
    args.action(config, args)


if __name__ == "__main__":
    main()
