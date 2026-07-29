from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from typing import cast

import discord

from alliancesim.adapters.inbound.discord.bot import (
    AllianceDiscordClient,
    EventActionView,
    EventButton,
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


class CapturingDiscordCommands:
    def __init__(self) -> None:
        self.start_call: tuple[str, str, str] | None = None

    async def start(self, user_id: str, name: str, interaction_id: str) -> MessageView:
        self.start_call = (user_id, name, interaction_id)
        return MessageView("Created", name)


class FakeDiscordResponse:
    def __init__(self) -> None:
        self.deferred = False

    async def defer(self, *, ephemeral: bool = False) -> None:
        assert ephemeral is True
        self.deferred = True

    def is_done(self) -> bool:
        return self.deferred


class FakeDiscordFollowup:
    def __init__(self) -> None:
        self.embeds: list[discord.Embed] = []

    async def send(self, *, embed: discord.Embed, ephemeral: bool, **_: object) -> None:
        assert ephemeral is True
        self.embeds.append(embed)


class FakeDiscordUser:
    id = 42


class FakeDiscordInteraction:
    id = 9001
    user = FakeDiscordUser()

    def __init__(self) -> None:
        self.response = FakeDiscordResponse()
        self.followup = FakeDiscordFollowup()


def test_discord_client_registers_mvp_slash_commands() -> None:
    commands = cast(ChatCommandAdapter, UnusedCommands())
    client = AllianceDiscordClient(commands, guild_id=123)
    names = {command.name for command in client.tree.get_commands(guild=discord.Object(id=123))}
    assert names == {"start", "status", "mine", "train", "events"}


async def test_discord_start_handler_defers_and_uses_followup() -> None:
    captured = CapturingDiscordCommands()
    client = AllianceDiscordClient(cast(ChatCommandAdapter, captured), guild_id=123)
    fake = FakeDiscordInteraction()
    await client.start_command(cast(discord.Interaction, fake), "Handler Union")
    assert fake.response.deferred is True
    assert captured.start_call == ("42", "Handler Union", "9001")
    assert fake.followup.embeds[0].title == "Created"


def test_discord_embed_preserves_platform_neutral_view() -> None:
    view = MessageView("Status", "Ready", (ViewField("Ore", "100"),))
    embed = discord_embed(view)
    assert embed.title == "Status"
    assert embed.description == "Ready"
    assert embed.fields[0].name == "Ore"
    assert embed.fields[0].value == "100"


def test_discord_event_actions_become_component_buttons() -> None:
    action_id = "event:00000000-0000-0000-0000-000000000001:take"
    view = EventActionView((ViewAction(action_id, "Take"),))
    assert view.timeout is None
    assert len(view.children) == 1
    dynamic = view.children[0]
    assert isinstance(dynamic, EventButton)
    assert dynamic.item.custom_id == action_id
    assert dynamic.item.label == "Take"


async def test_discord_event_button_can_be_reconstructed_after_restart() -> None:
    action_id = "event:00000000-0000-0000-0000-000000000001:take"
    item: discord.ui.Button[discord.ui.View] = discord.ui.Button(label="Take", custom_id=action_id)
    match = re.fullmatch(EventButton.__discord_ui_compiled_template__, action_id)
    assert match is not None
    dynamic = await EventButton.from_custom_id(cast(discord.Interaction, object()), item, match)
    assert dynamic.item.custom_id == action_id
    assert dynamic.item.label == "Take"


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
    ) -> bool:
        del outbox_id, now, error
        return False


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
