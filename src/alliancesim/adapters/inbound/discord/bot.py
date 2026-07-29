from __future__ import annotations

from collections.abc import Awaitable, Callable

import discord
from discord import app_commands

from alliancesim.application.chat_commands import ChatCommandAdapter
from alliancesim.application.views import MessageView, ViewAction


def discord_embed(view: MessageView) -> discord.Embed:
    colour = discord.Colour.red() if view.is_error else discord.Colour.blue()
    embed = discord.Embed(title=view.title, description=view.body, colour=colour)
    for field in view.fields:
        embed.add_field(name=field.name, value=field.value, inline=field.inline)
    return embed


class EventButton(discord.ui.Button[discord.ui.View]):
    def __init__(
        self,
        action: ViewAction,
        handler: Callable[[discord.Interaction, str], Awaitable[None]],
    ) -> None:
        super().__init__(
            style=discord.ButtonStyle.primary,
            label=action.label,
            custom_id=action.action_id,
        )
        self._action_id = action.action_id
        self._handler = handler

    async def callback(self, interaction: discord.Interaction) -> None:
        await self._handler(interaction, self._action_id)


class EventActionView(discord.ui.View):
    def __init__(
        self,
        actions: tuple[ViewAction, ...],
        handler: Callable[[discord.Interaction, str], Awaitable[None]],
    ) -> None:
        super().__init__(timeout=900)
        for action in actions:
            self.add_item(EventButton(action, handler))


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
            await interaction.response.send_message(
                embed=discord_embed(view),
                view=EventActionView(view.actions, self._handle_action),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(embed=discord_embed(view), ephemeral=True)

    async def _handle_action(self, interaction: discord.Interaction, action_id: str) -> None:
        result = await self._commands.resolve_action(str(interaction.user.id), action_id)
        await self._respond(interaction, result)

    async def start_command(self, interaction: discord.Interaction, name: str) -> None:
        view = await self._commands.start(str(interaction.user.id), name, str(interaction.id))
        await self._respond(interaction, view)

    async def status_command(self, interaction: discord.Interaction) -> None:
        view = await self._commands.status(str(interaction.user.id))
        await self._respond(interaction, view)

    async def mine_command(self, interaction: discord.Interaction) -> None:
        view = await self._commands.mine(str(interaction.user.id), str(interaction.id))
        await self._respond(interaction, view)

    async def train_command(self, interaction: discord.Interaction) -> None:
        view = await self._commands.train(str(interaction.user.id), str(interaction.id))
        await self._respond(interaction, view)

    async def events_command(self, interaction: discord.Interaction) -> None:
        view = await self._commands.events(str(interaction.user.id))
        await self._respond(interaction, view)
