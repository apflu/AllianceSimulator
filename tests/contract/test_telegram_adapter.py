from __future__ import annotations

from typing import cast

from aiogram.filters.command import CommandObject
from aiogram.types import Message

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
    def __init__(self) -> None:
        self.start_call: tuple[str, str, str] | None = None

    async def start(self, user_id: str, name: str, interaction_id: str) -> MessageView:
        self.start_call = (user_id, name, interaction_id)
        return MessageView("Created", name)


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
    assert fake.answers == ["Created\n\nHandler Union"]


def test_telegram_text_preserves_platform_neutral_view() -> None:
    view = MessageView("Status", "Ready", (ViewField("Ore", "100"),))
    assert telegram_text(view) == "Status\n\nReady\n\nOre\n100"


def test_telegram_event_actions_become_inline_buttons() -> None:
    view = MessageView("Event", "Choose", actions=(ViewAction("event:1:take", "Take"),))
    markup = telegram_markup(view)
    assert markup is not None
    assert markup.inline_keyboard[0][0].callback_data == "event:1:take"
