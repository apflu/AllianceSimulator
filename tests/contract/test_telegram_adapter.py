from __future__ import annotations

from typing import cast

import structlog
from aiogram.filters.command import CommandObject
from aiogram.types import CallbackQuery, Message

from alliancesim.adapters.inbound.telegram.bot import (
    AllianceTelegramRouter,
    telegram_markup,
    telegram_text,
)
from alliancesim.application.chat_commands import ChatCommandAdapter
from alliancesim.application.views import MessageView, ViewAction, ViewField


class UnusedCommands:
    """Router registration does not call the command adapter."""


class CapturingTelegramCommands:
    def __init__(self, sequence: list[str] | None = None) -> None:
        self.start_call: tuple[str, str, str] | None = None
        self.context: dict[str, object] = {}
        self._sequence = sequence

    async def start(self, user_id: str, name: str, interaction_id: str) -> MessageView:
        self.start_call = (user_id, name, interaction_id)
        self.context = structlog.contextvars.get_contextvars()
        return MessageView("Created", name)

    async def resolve_action(self, user_id: str, action_id: str) -> MessageView:
        assert user_id == "42"
        assert action_id == "event:00000000-0000-0000-0000-000000000001:take"
        if self._sequence is not None:
            self._sequence.append("resolve")
        return MessageView("Resolved", "Done")


class FakeTelegramUser:
    id = 42


class FakeTelegramChat:
    id = 700


class FakeTelegramMessage:
    from_user = FakeTelegramUser()
    chat = FakeTelegramChat()
    message_id = 11

    def __init__(self) -> None:
        self.answers: list[str] = []

    async def answer(self, text: str, **_: object) -> None:
        self.answers.append(text)


class FakeTelegramBot:
    def __init__(self, sequence: list[str]) -> None:
        self._sequence = sequence

    async def send_message(self, chat_id: int, text: str, **_: object) -> None:
        assert chat_id == 42
        assert text == "Resolved\n\nDone"
        self._sequence.append("send")


class FakeTelegramCallback:
    id = "callback-99"
    data = "event:00000000-0000-0000-0000-000000000001:take"
    from_user = FakeTelegramUser()

    def __init__(self, sequence: list[str]) -> None:
        self._sequence = sequence
        self.bot = FakeTelegramBot(sequence)

    async def answer(self, *_: object, **__: object) -> None:
        self._sequence.append("answer")


def test_telegram_router_registers_mvp_commands() -> None:
    commands = cast(ChatCommandAdapter, UnusedCommands())
    adapter = AllianceTelegramRouter(commands)
    assert len(adapter.router.message.handlers) == 5
    assert len(adapter.router.callback_query.handlers) == 1


async def test_telegram_start_handler_uses_stable_message_identity() -> None:
    captured = CapturingTelegramCommands()
    adapter = AllianceTelegramRouter(cast(ChatCommandAdapter, captured))
    fake = FakeTelegramMessage()
    command = CommandObject(command="start", args="Handler Union")
    await adapter.start_command(cast(Message, fake), command)
    assert captured.start_call == ("42", "Handler Union", "700:11")
    assert captured.context == {"platform": "telegram", "request_id": "700:11"}
    assert fake.answers == ["Created\n\nHandler Union"]


async def test_telegram_callback_is_acknowledged_before_processing() -> None:
    sequence: list[str] = []
    captured = CapturingTelegramCommands(sequence)
    adapter = AllianceTelegramRouter(cast(ChatCommandAdapter, captured))
    callback = FakeTelegramCallback(sequence)
    await adapter.action_callback(cast(CallbackQuery, callback))
    assert sequence == ["answer", "resolve", "send"]


def test_telegram_text_preserves_platform_neutral_view() -> None:
    view = MessageView("Status", "Ready", (ViewField("Ore", "100"),))
    assert telegram_text(view) == "Status\n\nReady\n\nOre\n100"


def test_telegram_event_actions_become_inline_buttons() -> None:
    view = MessageView("Event", "Choose", actions=(ViewAction("event:1:take", "Take"),))
    markup = telegram_markup(view)
    assert markup is not None
    assert markup.inline_keyboard[0][0].callback_data == "event:1:take"
