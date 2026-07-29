from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from alliancesim.adapters.outbound.persistence.database import Database
from alliancesim.adapters.outbound.persistence.game_store import SqlAlchemyGameStore
from alliancesim.adapters.outbound.persistence.models import Base
from alliancesim.application.errors import ConflictError, NotFoundError
from alliancesim.application.game_service import GameService
from alliancesim.domain.identity import Platform
from alliancesim.domain.mining import MiningRules

NOW = datetime(2026, 7, 30, 12, 0, tzinfo=UTC)


@asynccontextmanager
async def game_database(path: Path) -> AsyncGenerator[tuple[Database, SqlAlchemyGameStore]]:
    database = Database(f"sqlite+aiosqlite:///{path.as_posix()}")
    async with database.engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    try:
        yield database, SqlAlchemyGameStore(database.sessions)
    finally:
        await database.close()


async def test_full_mining_lifecycle_is_idempotent_and_persistent(tmp_path: Path) -> None:
    path = tmp_path / "game.sqlite3"
    rules = MiningRules(duration=timedelta(minutes=1), base_yield=100)
    async with game_database(path) as (_, store):
        service = GameService(store, clock=lambda: NOW, mining_rules=rules)
        created = await service.create_alliance(
            Platform.DISCORD, "player-1", "Outer Rim Union", "interaction-start-1"
        )
        duplicate = await service.create_alliance(
            Platform.DISCORD, "player-1", "Ignored Rename", "interaction-start-1"
        )
        assert created.created is True
        assert duplicate == type(duplicate)(created.alliance_id, "Outer Rim Union", False)

        initial = await service.get_status(Platform.DISCORD, "player-1")
        assert initial.character_name == "New Capsuleer"
        assert initial.ship_name == "Pioneer"
        assert initial.inventory == ()

        started = await service.start_mining(Platform.DISCORD, "player-1", "interaction-mine-1")
        duplicate_start = await service.start_mining(
            Platform.DISCORD, "player-1", "interaction-mine-1"
        )
        assert started.created is True
        assert duplicate_start.action_id == started.action_id
        assert duplicate_start.created is False
        assert started.finishes_at == NOW + timedelta(minutes=1)

        with pytest.raises(ConflictError, match="active action"):
            await service.start_mining(Platform.DISCORD, "player-1", "interaction-mine-2")

        assert (await store.complete_due_actions(NOW, limit=10)).count == 0
        batch = await store.complete_due_actions(NOW + timedelta(minutes=1), limit=10)
        assert batch.completed_action_ids == (started.action_id,)
        assert (await store.complete_due_actions(NOW + timedelta(minutes=2), limit=10)).count == 0

    async with game_database(path) as (_, restarted_store):
        restarted_service = GameService(restarted_store, clock=lambda: NOW, mining_rules=rules)
        status = await restarted_service.get_status(Platform.DISCORD, "player-1")
        assert status.active_action is None
        assert [(item.material_id, item.quantity) for item in status.inventory] == [
            ("raw-ore", 100)
        ]
        notifications = await restarted_store.claim_notifications(
            NOW + timedelta(minutes=1), limit=10
        )
        assert len(notifications) == 1
        assert notifications[0].event_type == "mining_completed"
        assert notifications[0].payload["quantity"] == 100
        await restarted_store.mark_notification_sent(
            notifications[0].outbox_id, NOW + timedelta(minutes=1)
        )
        assert (
            await restarted_store.claim_notifications(NOW + timedelta(minutes=2), limit=10)
        ) == ()


async def test_unknown_identity_cannot_query_or_mine(tmp_path: Path) -> None:
    async with game_database(tmp_path / "unknown.sqlite3") as (_, store):
        service = GameService(store, clock=lambda: NOW)
        with pytest.raises(NotFoundError, match="create an alliance"):
            await service.get_status(Platform.TELEGRAM, "missing")
        with pytest.raises(NotFoundError, match="create an alliance"):
            await service.start_mining(Platform.TELEGRAM, "missing", "missing-mine")


async def test_failed_notification_is_retried_after_backoff(tmp_path: Path) -> None:
    rules = MiningRules(duration=timedelta(seconds=1), base_yield=10)
    async with game_database(tmp_path / "retry.sqlite3") as (_, store):
        service = GameService(store, clock=lambda: NOW, mining_rules=rules)
        await service.create_alliance(Platform.DISCORD, "retry-user", "Retry Union", "start")
        await service.start_mining(Platform.DISCORD, "retry-user", "mine")
        await store.complete_due_actions(NOW + timedelta(seconds=1), limit=10)
        notification = (await store.claim_notifications(NOW + timedelta(seconds=1), limit=1))[0]
        await store.mark_notification_failed(
            notification.outbox_id, NOW + timedelta(seconds=1), "temporary outage"
        )
        assert (await store.claim_notifications(NOW + timedelta(seconds=2), limit=1)) == ()
        retried = await store.claim_notifications(NOW + timedelta(seconds=4), limit=1)
        assert len(retried) == 1
