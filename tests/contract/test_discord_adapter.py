from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import cast

import discord

from alliancesim.adapters.inbound.discord.bot import (
    AllianceDiscordClient,
    EventActionView,
    discord_embed,
)
from alliancesim.application.chat_commands import ChatCommandAdapter
from alliancesim.application.models import (
    AllianceCreated,
    AllianceStatus,
    CompletionBatch,
    CreateAllianceRequest,
    EventResolved,
    MiningStarted,
    PendingEvent,
    PendingNotification,
    PlatformRef,
    ResolveEventRequest,
    StartMiningRequest,
    StartTrainingRequest,
    TrainingStarted,
)
from alliancesim.application.views import MessageView, ViewAction, ViewField


class UnusedCommands:
    """The command tree only needs the adapter type during registration."""


def test_discord_client_registers_mvp_slash_commands() -> None:
    commands = cast(ChatCommandAdapter, UnusedCommands())
    client = AllianceDiscordClient(commands, guild_id=123)
    names = {command.name for command in client.tree.get_commands(guild=discord.Object(id=123))}
    assert names == {"start", "status", "mine", "train", "events"}


def test_discord_embed_preserves_platform_neutral_view() -> None:
    view = MessageView("Status", "Ready", (ViewField("Ore", "100"),))
    embed = discord_embed(view)
    assert embed.title == "Status"
    assert embed.description == "Ready"
    assert embed.fields[0].name == "Ore"
    assert embed.fields[0].value == "100"


def test_discord_event_actions_become_component_buttons() -> None:
    async def handler(_: discord.Interaction, action_id: str) -> None:
        del action_id

    view = EventActionView((ViewAction("event:1:take", "Take"),), handler)
    assert len(view.children) == 1
    button = view.children[0]
    assert isinstance(button, discord.ui.Button)
    assert button.custom_id == "event:1:take"
    assert button.label == "Take"


class StubStore:
    async def create_alliance(self, request: CreateAllianceRequest) -> AllianceCreated:
        return AllianceCreated(uuid.UUID(int=1), request.alliance_name, True)

    async def get_status(self, identity: PlatformRef) -> AllianceStatus:
        del identity
        return AllianceStatus(
            alliance_id=uuid.UUID(int=1),
            name="Test Alliance",
            character_id=uuid.UUID(int=2),
            character_name="Pilot",
            ship_id=uuid.UUID(int=3),
            ship_name="Pioneer",
            inventory=(),
            active_action=None,
        )

    async def start_mining(self, request: StartMiningRequest) -> MiningStarted:
        return MiningStarted(uuid.UUID(int=4), request.plan.finishes_at, 100, True)

    async def get_skill_level(self, identity: PlatformRef, skill_id: str) -> int:
        del identity, skill_id
        return 0

    async def start_training(self, request: StartTrainingRequest) -> TrainingStarted:
        return TrainingStarted(
            uuid.UUID(int=5),
            request.plan.skill_id,
            request.plan.target_level,
            request.plan.finishes_at,
            True,
        )

    async def list_pending_events(self, identity: PlatformRef) -> tuple[PendingEvent, ...]:
        del identity
        return ()

    async def resolve_event(self, request: ResolveEventRequest, now: datetime) -> EventResolved:
        raise AssertionError((request, now))

    async def expire_due_events(self, now: datetime, *, limit: int) -> int:
        del now, limit
        return 0

    async def complete_due_actions(self, now: datetime, *, limit: int) -> CompletionBatch:
        del now, limit
        return CompletionBatch(())

    async def claim_notifications(
        self, now: datetime, *, limit: int
    ) -> tuple[PendingNotification, ...]:
        del now, limit
        return ()

    async def mark_notification_sent(self, outbox_id: uuid.UUID, now: datetime) -> None:
        del outbox_id, now

    async def mark_notification_failed(
        self, outbox_id: uuid.UUID, now: datetime, error: str
    ) -> None:
        del outbox_id, now, error


async def test_discord_chat_commands_return_views_without_sdk_objects() -> None:
    from alliancesim.application.game_service import GameService
    from alliancesim.domain.identity import Platform

    service = GameService(StubStore(), clock=lambda: datetime(2026, 7, 30, tzinfo=UTC))
    commands = ChatCommandAdapter(service, Platform.DISCORD)
    created = await commands.start("42", "Test Alliance", "interaction-1")
    status = await commands.status("42")
    training = await commands.train("42", "interaction-2")
    events = await commands.events("42")
    assert created.title == "联盟已建立"
    assert status.title == "Test Alliance"
    assert training.title == "技能训练已开始"
    assert events.body == "目前没有待处理事件。"
