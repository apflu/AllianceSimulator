from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from typing import Any

import discord
import structlog
from discord import app_commands

from alliancesim.application.chat_commands import ChatCommandAdapter
from alliancesim.application.views import MessageView, ViewAction

logger = structlog.get_logger()


def discord_embed(view: MessageView) -> discord.Embed:
    colour = discord.Colour.red() if view.is_error else discord.Colour.blue()
    embed = discord.Embed(title=view.title, description=view.body, colour=colour)
    for field in view.fields:
        embed.add_field(name=field.name, value=field.value, inline=field.inline)
    return embed


class EventButton(
    discord.ui.DynamicItem[discord.ui.Button[discord.ui.View]],
    template=r"event:(?P<occurrence>[0-9a-fA-F-]{36}):(?P<option>[^:]{1,40})",
):
    def __init__(self, action: ViewAction) -> None:
        super().__init__(
            discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label=action.label,
                custom_id=action.action_id,
            )
        )
        self._action_id = action.action_id

    @classmethod
    async def from_custom_id(
        cls,
        interaction: discord.Interaction,
        item: discord.ui.Item[Any],
        match: re.Match[str],
        /,
    ) -> EventButton:
        del interaction
        if not isinstance(item, discord.ui.Button):
            raise TypeError("event action must be a Discord button")
        return cls(ViewAction(match.group(0), item.label or "选择"))

    async def callback(self, interaction: discord.Interaction) -> None:
        client = interaction.client
        if not isinstance(client, AllianceDiscordClient):
            raise RuntimeError("event action was dispatched by an unexpected client")
        await client.handle_event_action(interaction, self._action_id)


class EventActionView(discord.ui.View):
    def __init__(self, actions: tuple[ViewAction, ...]) -> None:
        super().__init__(timeout=None)
        for action in actions:
            self.add_item(EventButton(action))


class AllianceDiscordClient(discord.Client):
    def __init__(
        self,
        commands: ChatCommandAdapter,
        *,
        guild_id: int | None = None,
        on_close: Callable[[], Awaitable[None]] | None = None,
    ) -> None:
        super().__init__(intents=discord.Intents.none())
        self.tree = app_commands.CommandTree(self)
        self._commands = commands
        self._guild = discord.Object(id=guild_id) if guild_id is not None else None
        self._on_close = on_close
        self.add_dynamic_items(EventButton)
        self.tree.add_command(
            app_commands.Command(
                name="start",
                description="创建或查看你的联盟",
                callback=self.start_command,
            ),
            guild=self._guild,
        )
        self.tree.add_command(
            app_commands.Command(
                name="events",
                description="查看待处理联盟事件",
                callback=self.events_command,
            ),
            guild=self._guild,
        )
        self.tree.add_command(
            app_commands.Command(
                name="status",
                description="查看联盟状态",
                callback=self.status_command,
            ),
            guild=self._guild,
        )
        self.tree.add_command(
            app_commands.Command(
                name="mine",
                description="开始一次采矿行动",
                callback=self.mine_command,
            ),
            guild=self._guild,
        )
        self.tree.add_command(
            app_commands.Command(
                name="train",
                description="训练采矿技能",
                callback=self.train_command,
            ),
            guild=self._guild,
        )

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=self._guild)

    async def close(self) -> None:
        try:
            await super().close()
        finally:
            if self._on_close is not None:
                await self._on_close()

    async def _respond(self, interaction: discord.Interaction, view: MessageView) -> None:
        if view.actions:
            action_view = EventActionView(view.actions)
            if interaction.response.is_done():
                await interaction.followup.send(
                    embed=discord_embed(view), view=action_view, ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    embed=discord_embed(view), view=action_view, ephemeral=True
                )
        else:
            if interaction.response.is_done():
                await interaction.followup.send(embed=discord_embed(view), ephemeral=True)
            else:
                await interaction.response.send_message(embed=discord_embed(view), ephemeral=True)

    async def _run_command(
        self,
        interaction: discord.Interaction,
        command: str,
        operation: Callable[[], Awaitable[MessageView]],
        *,
        action_id: str | None = None,
    ) -> None:
        with structlog.contextvars.bound_contextvars(
            request_id=str(interaction.id), platform="discord"
        ):
            logger.info("platform_command_started", command=command, action_id=action_id)
            view = await operation()
            await self._respond(interaction, view)
            logger.info(
                "platform_command_completed",
                command=command,
                action_id=action_id,
                is_error=view.is_error,
            )

    async def handle_event_action(self, interaction: discord.Interaction, action_id: str) -> None:
        await interaction.response.defer(ephemeral=True)
        await self._run_command(
            interaction,
            "resolve_event",
            lambda: self._commands.resolve_action(str(interaction.user.id), action_id),
            action_id=action_id,
        )

    async def start_command(self, interaction: discord.Interaction, name: str) -> None:
        await interaction.response.defer(ephemeral=True)
        await self._run_command(
            interaction,
            "start",
            lambda: self._commands.start(str(interaction.user.id), name, str(interaction.id)),
        )

    async def status_command(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        await self._run_command(
            interaction, "status", lambda: self._commands.status(str(interaction.user.id))
        )

    async def mine_command(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        await self._run_command(
            interaction,
            "mine",
            lambda: self._commands.mine(str(interaction.user.id), str(interaction.id)),
        )

    async def train_command(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        await self._run_command(
            interaction,
            "train",
            lambda: self._commands.train(str(interaction.user.id), str(interaction.id)),
        )

    async def events_command(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        await self._run_command(
            interaction, "events", lambda: self._commands.events(str(interaction.user.id))
        )
