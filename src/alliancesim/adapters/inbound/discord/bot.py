from __future__ import annotations

import discord
from discord import app_commands

from alliancesim.application.chat_commands import ChatCommandAdapter
from alliancesim.application.views import MessageView


def discord_embed(view: MessageView) -> discord.Embed:
    colour = discord.Colour.red() if view.is_error else discord.Colour.blue()
    embed = discord.Embed(title=view.title, description=view.body, colour=colour)
    for field in view.fields:
        embed.add_field(name=field.name, value=field.value, inline=field.inline)
    return embed


class AllianceDiscordClient(discord.Client):
    def __init__(self, commands: ChatCommandAdapter, *, guild_id: int | None = None) -> None:
        super().__init__(intents=discord.Intents.none())
        self.tree = app_commands.CommandTree(self)
        self._commands = commands
        self._guild = discord.Object(id=guild_id) if guild_id is not None else None
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

    @staticmethod
    async def _respond(interaction: discord.Interaction, view: MessageView) -> None:
        await interaction.response.send_message(embed=discord_embed(view), ephemeral=True)

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
