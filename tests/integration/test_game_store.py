from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from alliancesim.adapters.outbound.persistence.database import Database
from alliancesim.adapters.outbound.persistence.game_store import (
    MAX_NOTIFICATION_ATTEMPTS,
    SqlAlchemyGameStore,
)
from alliancesim.adapters.outbound.persistence.models import Base
from alliancesim.application.errors import ConflictError, NotFoundError
from alliancesim.application.game_service import GameService
from alliancesim.domain.identity import Platform
from alliancesim.domain.mining import MiningRules
from alliancesim.domain.training import SkillRules

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

    async with game_database(path) as (_, restarted_store):
        restarted_service = GameService(restarted_store, clock=lambda: NOW, mining_rules=rules)
        batch = await restarted_store.complete_due_actions(NOW + timedelta(minutes=1), limit=10)
        assert batch.completed_action_ids == (started.action_id,)
        assert (
            await restarted_store.complete_due_actions(NOW + timedelta(minutes=2), limit=10)
        ).count == 0

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


async def test_notification_stops_after_terminal_failure(tmp_path: Path) -> None:
    rules = MiningRules(duration=timedelta(seconds=1), base_yield=10)
    async with game_database(tmp_path / "terminal-notification.sqlite3") as (_, store):
        service = GameService(store, clock=lambda: NOW, mining_rules=rules)
        await service.create_alliance(Platform.TELEGRAM, "dead-letter", "Final Union", "start")
        await service.start_mining(Platform.TELEGRAM, "dead-letter", "mine")
        current = NOW + timedelta(seconds=1)
        await store.complete_due_actions(current, limit=10)

        for attempt in range(1, MAX_NOTIFICATION_ATTEMPTS + 1):
            claimed = await store.claim_notifications(current, limit=1)
            assert len(claimed) == 1
            terminal = await store.mark_notification_failed(
                claimed[0].outbox_id, current, "Telegram API returned HTTP 403"
            )
            assert terminal is (attempt == MAX_NOTIFICATION_ATTEMPTS)
            current += timedelta(minutes=10)

        assert await store.claim_notifications(current, limit=1) == ()


async def test_discord_and_telegram_produce_equivalent_game_state(tmp_path: Path) -> None:
    rules = MiningRules(duration=timedelta(minutes=3), base_yield=75)
    async with game_database(tmp_path / "parity.sqlite3") as (_, store):
        service = GameService(store, clock=lambda: NOW, mining_rules=rules)
        for platform, user_id in (
            (Platform.DISCORD, "discord-user"),
            (Platform.TELEGRAM, "telegram-user"),
        ):
            await service.create_alliance(platform, user_id, "Parity Union", f"{platform}-start")
            await service.start_mining(platform, user_id, f"{platform}-mine")

        discord_status = await service.get_status(Platform.DISCORD, "discord-user")
        telegram_status = await service.get_status(Platform.TELEGRAM, "telegram-user")
        assert discord_status.name == telegram_status.name
        assert discord_status.character_name == telegram_status.character_name
        assert discord_status.ship_name == telegram_status.ship_name
        assert discord_status.active_action is not None
        assert telegram_status.active_action is not None
        assert discord_status.active_action.action_type == telegram_status.active_action.action_type
        assert discord_status.active_action.finishes_at == telegram_status.active_action.finishes_at


async def test_training_persists_and_increases_future_mining_yield(tmp_path: Path) -> None:
    current_time = [NOW]
    mining_rules = MiningRules(duration=timedelta(minutes=1), base_yield=100)
    skill_rules = SkillRules("mining-operations", timedelta(minutes=2), 5, 1_000)
    path = tmp_path / "training.sqlite3"
    async with game_database(path) as (_, store):
        service = GameService(
            store,
            clock=lambda: current_time[0],
            mining_rules=mining_rules,
            skill_rules=skill_rules,
        )
        await service.create_alliance(Platform.DISCORD, "trainee", "Training Union", "start")
        training = await service.start_training(Platform.DISCORD, "trainee", "train-1")
        duplicate = await service.start_training(Platform.DISCORD, "trainee", "train-1")
        assert training.target_level == 1
        assert duplicate.action_id == training.action_id
        assert duplicate.created is False

    async with game_database(path) as (_, store):
        restarted_service = GameService(
            store,
            clock=lambda: current_time[0],
            mining_rules=mining_rules,
            skill_rules=skill_rules,
        )
        current_time[0] = NOW + timedelta(minutes=2)
        assert (await store.complete_due_actions(current_time[0], limit=10)).count == 1
        status = await restarted_service.get_status(Platform.DISCORD, "trainee")
        assert [(skill.skill_id, skill.level) for skill in status.skills] == [
            ("mining-operations", 1)
        ]

        mining = await restarted_service.start_mining(
            Platform.DISCORD, "trainee", "mine-after-training"
        )
        assert mining.yield_quantity == 110


async def test_mining_triggers_resolvable_idempotent_event(tmp_path: Path) -> None:
    rules = MiningRules(duration=timedelta(seconds=1), base_yield=100)
    current_time = [NOW]
    async with game_database(tmp_path / "event.sqlite3") as (_, store):
        service = GameService(store, clock=lambda: current_time[0], mining_rules=rules)
        await service.create_alliance(Platform.DISCORD, "event-user", "Event Union", "start")
        await service.start_mining(Platform.DISCORD, "event-user", "mine")
        current_time[0] = NOW + timedelta(seconds=1)
        await store.complete_due_actions(current_time[0], limit=10)

        events = await service.list_pending_events(Platform.DISCORD, "event-user")
        assert len(events) == 1
        assert events[0].template_id == "ore-discovery"
        assert {option.option_id for option in events[0].options} == {"refine", "analyze"}

        action_id = f"event:{events[0].occurrence_id}:analyze"
        resolved = await service.resolve_event(
            Platform.DISCORD,
            "event-user",
            events[0].occurrence_id,
            "analyze",
            action_id,
        )
        duplicate = await service.resolve_event(
            Platform.DISCORD,
            "event-user",
            events[0].occurrence_id,
            "analyze",
            action_id,
        )
        assert resolved.applied is True
        assert duplicate.applied is False
        assert await service.list_pending_events(Platform.DISCORD, "event-user") == ()
        status = await service.get_status(Platform.DISCORD, "event-user")
        assert [(item.material_id, item.quantity) for item in status.inventory] == [
            ("raw-ore", 100),
            ("research-data", 1),
        ]

        with pytest.raises(ConflictError, match="no longer pending"):
            await service.resolve_event(
                Platform.DISCORD,
                "event-user",
                events[0].occurrence_id,
                "refine",
                f"event:{events[0].occurrence_id}:refine",
            )


async def test_event_timeout_applies_default_result_once(tmp_path: Path) -> None:
    rules = MiningRules(duration=timedelta(seconds=1), base_yield=100)
    current_time = [NOW]
    async with game_database(tmp_path / "event-timeout.sqlite3") as (_, store):
        service = GameService(store, clock=lambda: current_time[0], mining_rules=rules)
        await service.create_alliance(Platform.TELEGRAM, "timeout-user", "Timeout Union", "start")
        await service.start_mining(Platform.TELEGRAM, "timeout-user", "mine")
        current_time[0] = NOW + timedelta(seconds=1)
        await store.complete_due_actions(current_time[0], limit=10)
        assert len(await service.list_pending_events(Platform.TELEGRAM, "timeout-user")) == 1

        current_time[0] += timedelta(hours=24)
        assert await store.expire_due_events(current_time[0], limit=10) == 1
        assert await store.expire_due_events(current_time[0], limit=10) == 0
        assert await service.list_pending_events(Platform.TELEGRAM, "timeout-user") == ()
        status = await service.get_status(Platform.TELEGRAM, "timeout-user")
        assert [(item.material_id, item.quantity) for item in status.inventory] == [
            ("raw-ore", 150)
        ]
