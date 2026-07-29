from __future__ import annotations

from typing import cast

from alliancesim.adapters.inbound.telegram.bot import (
    AllianceTelegramRouter,
    telegram_markup,
    telegram_text,
)
from alliancesim.application.chat_commands import ChatCommandAdapter
from alliancesim.application.views import MessageView, ViewAction, ViewField


class UnusedCommands:
    """Router registration does not call the command adapter."""


def test_telegram_router_registers_mvp_commands() -> None:
    commands = cast(ChatCommandAdapter, UnusedCommands())
    adapter = AllianceTelegramRouter(commands)
    assert len(adapter.router.message.handlers) == 5
    assert len(adapter.router.callback_query.handlers) == 1


def test_telegram_text_preserves_platform_neutral_view() -> None:
    view = MessageView("Status", "Ready", (ViewField("Ore", "100"),))
    assert telegram_text(view) == "Status\n\nReady\n\nOre\n100"


def test_telegram_event_actions_become_inline_buttons() -> None:
    view = MessageView("Event", "Choose", actions=(ViewAction("event:1:take", "Take"),))
    markup = telegram_markup(view)
    assert markup is not None
    assert markup.inline_keyboard[0][0].callback_data == "event:1:take"
