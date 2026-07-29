from __future__ import annotations

from alliancesim.adapters.inbound.discord.bot import AllianceDiscordClient
from alliancesim.adapters.outbound.persistence.database import Database
from alliancesim.adapters.outbound.persistence.game_store import SqlAlchemyGameStore
from alliancesim.application.chat_commands import ChatCommandAdapter
from alliancesim.application.game_service import GameService
from alliancesim.bootstrap.logging import configure_logging
from alliancesim.bootstrap.settings import get_settings
from alliancesim.domain.identity import Platform


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    if settings.discord_token is None:
        raise RuntimeError("ASIM_DISCORD_TOKEN is required")
    database = Database(settings.database_url)
    store = SqlAlchemyGameStore(database.sessions)
    commands = ChatCommandAdapter(GameService(store), Platform.DISCORD)
    client = AllianceDiscordClient(
        commands,
        guild_id=settings.discord_guild_id,
        on_close=database.close,
    )
    client.run(settings.discord_token.get_secret_value(), log_handler=None)


if __name__ == "__main__":
    main()
