from __future__ import annotations

import asyncio
import os
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from alembic import command
from alembic.config import Config

from alliancesim.adapters.outbound.persistence.database import Database
from alliancesim.adapters.outbound.persistence.game_store import SqlAlchemyGameStore
from alliancesim.application.game_service import GameService
from alliancesim.domain.identity import Platform
from alliancesim.domain.mining import MiningRules

POSTGRES_URL = os.getenv("ASIM_TEST_POSTGRES_URL")
pytestmark = pytest.mark.skipif(
    POSTGRES_URL is None, reason="PostgreSQL test URL is not configured"
)


def alembic_config() -> Config:
    if POSTGRES_URL is None:
        raise RuntimeError("ASIM_TEST_POSTGRES_URL is required")
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", POSTGRES_URL)
    return config


@pytest.fixture(scope="module", autouse=True)
def ensure_postgres_schema() -> Iterator[None]:
    command.upgrade(alembic_config(), "head")
    yield


@pytest.mark.postgres
def test_postgres_migrations_downgrade_and_upgrade() -> None:
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    command.downgrade(config, "base")
    command.upgrade(config, "head")


@pytest.mark.postgres
async def test_postgres_workers_settle_one_action_exactly_once() -> None:
    if POSTGRES_URL is None:
        raise RuntimeError("ASIM_TEST_POSTGRES_URL is required")
    database_one = Database(POSTGRES_URL)
    database_two = Database(POSTGRES_URL)
    store_one = SqlAlchemyGameStore(database_one.sessions)
    store_two = SqlAlchemyGameStore(database_two.sessions)
    now = datetime(2026, 7, 30, tzinfo=UTC)
    user_id = f"postgres-{uuid.uuid4()}"
    try:
        service = GameService(
            store_one,
            clock=lambda: now,
            mining_rules=MiningRules(duration=timedelta(seconds=1), base_yield=100),
        )
        await service.create_alliance(Platform.DISCORD, user_id, "Concurrent Union", "start")
        await service.start_mining(Platform.DISCORD, user_id, "mine")
        batches = await asyncio.gather(
            store_one.complete_due_actions(now + timedelta(seconds=1), limit=1),
            store_two.complete_due_actions(now + timedelta(seconds=1), limit=1),
        )
        assert sum(batch.count for batch in batches) == 1
        status = await service.get_status(Platform.DISCORD, user_id)
        assert [(item.material_id, item.quantity) for item in status.inventory] == [
            ("raw-ore", 100)
        ]
    finally:
        await database_one.close()
        await database_two.close()
