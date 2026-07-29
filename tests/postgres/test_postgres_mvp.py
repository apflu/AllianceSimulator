from __future__ import annotations

import asyncio
import os
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
import sqlalchemy as sa
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


async def create_mining_and_training_history() -> tuple[uuid.UUID, uuid.UUID]:
    if POSTGRES_URL is None:
        raise RuntimeError("ASIM_TEST_POSTGRES_URL is required")
    database = Database(POSTGRES_URL)
    store = SqlAlchemyGameStore(database.sessions)
    now = datetime(2026, 7, 30, tzinfo=UTC)
    user_id = f"downgrade-{uuid.uuid4()}"
    try:
        service = GameService(store, clock=lambda: now)
        await service.create_alliance(Platform.TELEGRAM, user_id, "Downgrade Union", "start")
        mining = await service.start_mining(Platform.TELEGRAM, user_id, "mine")
        await store.complete_due_actions(now + timedelta(minutes=1), limit=10)
        training = await service.start_training(Platform.TELEGRAM, user_id, "train")
        await store.complete_due_actions(now + timedelta(minutes=2), limit=10)
        return mining.action_id, training.action_id
    finally:
        await database.close()


async def downgraded_action_types(
    mining_action_id: uuid.UUID, training_action_id: uuid.UUID
) -> tuple[str | None, str | None, set[uuid.UUID]]:
    if POSTGRES_URL is None:
        raise RuntimeError("ASIM_TEST_POSTGRES_URL is required")
    database = Database(POSTGRES_URL)
    try:
        async with database.engine.connect() as connection:
            actions = await connection.execute(
                sa.text(
                    "SELECT id, action_type FROM timed_actions "
                    "WHERE id IN (:mining_id, :training_id)"
                ),
                {"mining_id": mining_action_id, "training_id": training_action_id},
            )
            action_types = {row.id: row.action_type for row in actions}
            notifications = await connection.execute(
                sa.text(
                    "SELECT source_action_id FROM notification_outbox "
                    "WHERE source_action_id IN (:mining_id, :training_id)"
                ),
                {"mining_id": mining_action_id, "training_id": training_action_id},
            )
            return (
                action_types.get(mining_action_id),
                action_types.get(training_action_id),
                {row.source_action_id for row in notifications},
            )
    finally:
        await database.close()


@pytest.mark.postgres
def test_training_history_can_downgrade_to_mining_only_schema() -> None:
    config = alembic_config()
    mining_action_id, training_action_id = asyncio.run(create_mining_and_training_history())
    try:
        command.downgrade(config, "20260730_0002")
        mining_type, training_type, notification_action_ids = asyncio.run(
            downgraded_action_types(mining_action_id, training_action_id)
        )
        assert mining_type == "mining"
        assert training_type is None
        assert notification_action_ids == {mining_action_id}
    finally:
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
