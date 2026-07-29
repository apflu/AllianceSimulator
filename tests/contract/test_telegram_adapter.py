from __future__ import annotations

from typing import cast

from alliancesim.adapters.inbound.telegram.bot import AllianceTelegramRouter, telegram_text
from alliancesim.application.chat_commands import ChatCommandAdapter
from alliancesim.application.views import MessageView, ViewField


class UnusedCommands:
    """Router registration does not call the command adapter."""


def test_telegram_router_registers_mvp_commands() -> None:
    commands = cast(ChatCommandAdapter, UnusedCommands())
    adapter = AllianceTelegramRouter(commands)
    assert len(adapter.router.message.handlers) == 3


def test_telegram_text_preserves_platform_neutral_view() -> None:
    view = MessageView("Status", "Ready", (ViewField("Ore", "100"),))
    assert telegram_text(view) == "Status\n\nReady\n\nOre\n100"
