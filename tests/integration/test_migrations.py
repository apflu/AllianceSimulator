import sqlite3
from pathlib import Path

from alembic import command
from alembic.config import Config


def test_migrations_upgrade_downgrade_and_upgrade(tmp_path: Path) -> None:
    database_path = tmp_path / "migration-test.sqlite3"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite+aiosqlite:///{database_path.as_posix()}")

    command.upgrade(config, "head")
    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
    assert {
        "players",
        "platform_identities",
        "alliances",
        "characters",
        "character_skills",
        "ships",
        "inventory_items",
        "timed_actions",
        "notification_outbox",
        "event_occurrences",
    } <= tables

    command.downgrade(config, "base")
    command.upgrade(config, "head")
